from pydub import AudioSegment
import subprocess, os
import librosa
import soundfile as sf


def dk_effects(mp3_path):
    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    reverbed = base_path + "_reverb.wav"
    subprocess.run([
        'sox', working_path, reverbed,
        'reverb', '50', '50', '75', '100', '25', '-5',
    ], check=True)
    working_path = reverbed

    bassed = base_path + "_bassed.wav"

    subprocess.run([
        'sox', working_path, bassed,
        'bass', '10',
        'gain', '2'], check=True)

    working_path = bassed


    tremmed = base_path + "_tremolo.wav"
    subprocess.run(['sox', working_path, tremmed,
                    'tremolo', '200'], check=True)
    working_path = tremmed


    y, sr = librosa.load(working_path, sr=None)
    processed = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=-0.50) #raspy voice

    # Save processed audio to temp wav file
    temp_final_wav = base_path + "_final.wav"
    sf.write(temp_final_wav, processed, sr)

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(temp_final_wav)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def robot_effects(mp3_path):
    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run(['sox', working_path, changed,
                    'tremolo', '100000',
                    'pitch', '-150',
                    'lowpass', '4000',      # Remove high frequencies
                    'gain', '-n',], check=True)
    working_path = changed


    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))


def ghost_effects(mp3_path):
    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run([
        'sox', working_path, changed,
        'reverb', '100', '70', '50', '80', '50', '0',
    ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def undead_effects(mp3_path):

    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run([
        'sox', working_path, changed,
        'reverb', '40', '40', '40', '50', '25', '-5'
    ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def demon_effects(mp3_path):

    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run([
        'sox', working_path, changed,
        'pitch', '-100',
        'reverb', '32', '40', '40', '50', '25', '-5'
    ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def ethereal_effects(mp3_path):

    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run([
        'sox', working_path, changed,
        'reverb', '50', '60', '100', '100', '100', '-6'
    ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def giant_effects(mp3_path, voice):

    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    if voice in (["ogrila_ogre",'ogre_male']):
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '-300',
            'tempo', '0.85',
        ], check=True)
    else:
        subprocess.run([
            'sox', working_path, changed,
            'pitch', '-100',
            'tempo', '1.2',
        ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))
def small_effects(mp3_path):

    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run([
        'sox', working_path, changed,
        'pitch', '400'
    ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def earthen_effects(mp3_path):

    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run([
       'sox', working_path, changed,
       'pitch', '-25',
       'gain', '2',
    ], check=True)
    working_path = changed

    y, sr = librosa.load(working_path, sr=None)
    processed = librosa.effects.pitch_shift(y=y, sr=sr, n_steps=-1.50) #for raspy voice

    # Save processed audio to temp wav file
    temp_final_wav = base_path + "_final.wav"
    sf.write(temp_final_wav, processed, sr)

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(temp_final_wav)
    final.export(mp3_path, format="mp3", bitrate="64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))

def naaru_effects(mp3_path):
    # Load the mp3
    sound = AudioSegment.from_file(mp3_path)

    # Work in-place using temporary intermediate files with .wav extension

    base_path = os.path.join(mp3_path[:-4])  # strip .mp3
    print(base_path)
    working_path = base_path + "_proc.wav"
    sound.export(working_path, format="wav")

    changed = base_path + "_changed.wav"
    subprocess.run([
       'sox', working_path, changed,
       'pitch', '-150',
       'tremolo','100',
       'reverb', '60', '50', '60', '100', '50', '-5',
       'gain', '-n',

    ], check=True)
    working_path = changed

    # Final: overwrite original .mp3 with processed audio
    final = AudioSegment.from_file(working_path)
    final.export(mp3_path, format="mp3", bitrate = "64k")

    # Clean up temp wavs
    for f in os.listdir(os.path.dirname(mp3_path)):
        if f.startswith(os.path.basename(base_path)) and f.endswith(".wav"):
            os.remove(os.path.join(os.path.dirname(mp3_path), f))
