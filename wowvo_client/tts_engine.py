import sys, types
import uuid
import os
import torch
import soundfile as sf
from torch.serialization import add_safe_globals
from TTS.tts.configs.xtts_config import XttsConfig
from TTS.tts.models.xtts import Xtts, XttsAudioConfig, XttsArgs, load_audio
from TTS.config.shared_configs import BaseDatasetConfig
import numpy as np
import pysbd
from typing import List
from scipy.io import wavfile
import threading

from rvc.modules.vc.modules import VC
from rvc.configs.config import Config

# Global model cache
default_model = None
config = Config()
vc = VC(config)

loaded_models = {}
loaded_models_lock = threading.Lock()

latents_cache = {}
latents_cache_lock = threading.Lock()

gpu_semaphore = threading.Semaphore(2)  # allow 2 concurrent synths

# pytorch requirement to add safe globals
add_safe_globals([
    XttsConfig, XttsAudioConfig, XttsArgs, BaseDatasetConfig,
])
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

def merge_short_fragments(chunks, min_length=15):
    """
    Merge very short chunks (e.g. 'To.', 'All.') with the previous one
    if they're too short to stand alone.
    """
    merged = []
    buffer = ""

    for chunk in chunks:
        stripped = chunk.strip()
        # If the current chunk is very short, merge it into buffer
        if len(stripped) < min_length and merged:
            merged[-1] = merged[-1].rstrip() + " " + stripped  # attach to previous
        else:
            merged.append(stripped)
    return merged


def split_into_sentences(text: str, lang: str = "en") -> List[str]:
    # If text is short enough, skip splitting entirely
    if len(text) <= 150:
        return [text]

    # Otherwise, use pysbd for sentence segmentation
    segmenter = pysbd.Segmenter(language=lang, clean=True)
    sentences = segmenter.segment(text)

    # Post-process each sentence: remove commas if <= 60 chars
    sentences = [
        s.replace(",", "") if len(s) <= 60 else s
        for s in sentences
    ]
    return sentences


def get_or_create_latents(model, speaker_key, speaker_wav):
    if speaker_key not in latents_cache:
        gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(speaker_wav)
        latents_cache[speaker_key] = (gpt_cond_latent, speaker_embedding)
    return latents_cache[speaker_key]

def load_default():
    global default_model, vc
    print("🔍 Loading default XTTS model from fine_tuned/base")

    base_dir = "fine_tuned/base"
    config_path = os.path.join(base_dir, "config.json")
    vocab_path = os.path.join(base_dir, "vocab.json")
    speakers_path = os.path.join(base_dir, "speakers_xtts.pth")

    config = XttsConfig()
    config.load_json(config_path)

    model = Xtts.init_from_config(config)
    model.load_checkpoint(
        config,
        checkpoint_dir=base_dir,
        speaker_file_path=speakers_path,
        vocab_path=vocab_path,
        eval=True,
    )
    model.to(DEVICE)

    default_model = model
    print("✅ Default XTTS model loaded from local base folder.")
load_default()

class TTSEngine:
    def __init__(self):
        self.OUTPUT_DIR = "output"

    def make_output_dir(self):
        os.makedirs(self.OUTPUT_DIR, exist_ok=True)

    def make_output_path(self, audio: str):
        self.output_path = os.path.join(self.OUTPUT_DIR, audio)
        return self.output_path


    def synthesize(
        self,
        text: str = None,
        speaker_wav: str = None,
        language: str = "en",
        model_dir: str = None,
        speaker_id: str = None,
        voice_name: str = None,

        # XTTS params
        temperature: float = 0.75,
        length_penalty: float = 1.2,
        repetition_penalty: float = 10.0,
        top_k: int = 1,
        top_p: float = 1.0,
        speed: float = 1.05,

        # RVC params
        f0_up_key: int = 0,
        f0_method: str = "rmvpe",
        index_rate: float = 0.70,
        filter_radius: int = 3,
        resample_sr: int = 0,
        rms_mix_rate: float = 1,
        protect: float = 0.25
    ):

            self.make_output_dir()

            global loaded_models, default_model
            # Save speaker reference audio
            ref_path = os.path.join(f"{speaker_wav}")
            audio = load_audio(ref_path, 22050)

            # Choose model
            if model_dir:
                model_key = os.path.abspath(model_dir)
                with gpu_semaphore:
                    if model_key not in loaded_models:

                        print(f"🔍 Loading fine-tuned model from {model_dir}")
                        config_path = os.path.join(model_dir, "config.json")
                        vocab_path = os.path.join(model_dir, "vocab.json")   # fine-tuned model

                        speakers_path = os.path.join(model_dir, "speakers_xtts.pth")

                        config = XttsConfig()
                        config.load_json(config_path)

                        model = Xtts.init_from_config(config)
                        model.load_checkpoint(
                            config,
                            checkpoint_dir=model_dir,
                            speaker_file_path=speakers_path,
                            vocab_path=vocab_path,
                            eval=True
                        )
                        model.to(DEVICE)
                        loaded_models[model_key] = model
                    tts = loaded_models.get(model_key, default_model)

            else:
                tts = default_model
            # Prune cache: keep only default and the current model_key
            keys_to_keep = set()
            if model_dir:
                keys_to_keep.add(model_key)
            # default_model is stored separately, so we don't remove it
            keys_to_remove = []
            with loaded_models_lock:
                for key in list(loaded_models.keys()):
                    if key not in keys_to_keep:
                        print(f"🧹 Unloading model from cache: {key}")
                        # remove mapping from dict now (so other threads won't try to use it)
                        model_obj = loaded_models.pop(key, None)
                        if model_obj is not None:
                            keys_to_remove.append((key, model_obj))

            for key, model_obj in keys_to_remove:
                try:
                    print(f"🧹 Unloading model from cache: {key}")
                    # move off GPU
                    model_obj.to("cpu")
                except Exception as e:
                    print(f"⚠️ Error moving {key} to CPU: {e}")
                finally:
                    # free cuda cache after model moved
                    try:
                        torch.cuda.empty_cache()
                    except Exception:
                        pass


            # Generate audio
            #This is why we need an inherited function, this needs to be passed back to TTSProcessor to export the file with its name to its final folder
            output_path = self.make_output_path(f"{uuid.uuid4()}.wav")

            if speaker_id and speaker_id in tts.speaker_manager.speakers:
                # ✅ Inbuild / fine-tuned speaker from speakers_xtts.pth
                speaker_id = ref_path
                gpt_cond_latent, speaker_embedding = tts.speaker_manager.speakers[speaker_id].values()
            else:
                # ✅ On-the-fly from reference wav, cached
                gpt_cond_latent, speaker_embedding = get_or_create_latents(tts, ref_path, ref_path)

            chunks = split_into_sentences(text)
            chunks = merge_short_fragments(chunks)
            print(chunks)

            #default value from slider in webui (10) interpreted as int so we force as float
            repetition_penalty = float(repetition_penalty)

            all_audio = []
            for chunk in chunks:
                with gpu_semaphore:
                    wav = tts.inference(
                        text=chunk,
                        language=language,
                        gpt_cond_latent = gpt_cond_latent,
                        speaker_embedding = speaker_embedding,
                        enable_text_splitting = False,
                        temperature = temperature,
                        length_penalty = length_penalty,
                        repetition_penalty = repetition_penalty,
                        top_k = top_k,
                        top_p = top_p,
                        speed = speed
                    )["wav"]
                    all_audio.append(wav)
                final_audio = np.concatenate(all_audio)
                sf.write(output_path, final_audio, 24000)  # XTTS uses 24kHz

            # Base path where RVC models are stored
            rvc_base = "fine_tuned/_rvc"
            rvc_model_path = os.path.join(rvc_base,"weights", f"{voice_name}.pth")
            rvc_index_path = os.path.join(rvc_base,"indices", f"{voice_name}.index")

            # Set environment variable for RVC
            os.environ.setdefault("rmvpe_root", "rvc/assets/rmvpe")

            if os.path.isfile(rvc_model_path):
                print(f"🎤 Running RVC post-processing for {voice_name}")

                # Load the RVC model if needed
                if not hasattr(vc, "model") or vc.model_path != rvc_model_path:
                    vc.get_vc(rvc_model_path)
                file_index = rvc_index_path if os.path.isfile(rvc_index_path) else None
                # Apply conversion
                info, audio_data = vc.vc_single(
                    sid=0,
                    input_audio_path=output_path,
                    f0_up_key=f0_up_key,
                    f0_file=None,
                    f0_method=f0_method,  # or "crepe"
                    file_index=file_index,
                    file_index2="",
                    index_rate=index_rate,
                    filter_radius=3,
                    resample_sr=resample_sr,
                    rms_mix_rate=1,
                    protect=protect
                )

                #audio = np.array(audio)
                if audio_data is None:
                    print(f"Error in voice conversion: {info}")
                    return  # or handle error appropriately
                sr, audio = audio_data

                # overwrite output_path with converted audio
                wavfile.write(output_path, sr, audio)
                return output_path
            else:
                print(f"⚠️ No RVC model found for {voice_name} at {rvc_model_path}")
                sf.write(output_path, final_audio, 24000),
                return output_path
