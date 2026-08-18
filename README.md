# WoW Voiceover: TBC \& WoTLK

This is an unofficial expansion of [WoWVoiceOver](https://github.com/mrthinger/wow-voiceover). It includes:

* Extra quests and gossip from Vanilla (item, gameobjects, and NPCs with custom models).
* Voiceover files for The Burning Crusade
* Voiceover files for Wrath of the Lich King

Based on the original Vanilla Voiceover, using [XTTS](https://huggingface.co/coqui/XTTS-v2) and [RVC](https://github.com/RVC-Project/Retrieval-based-Voice-Conversion-WebUI) for audio generation.

This repo currently has the code used to generate the VO files. for the actual Addon files, please refer to the project page on [CurseForge](https://www.curseforge.com/wow/addons/voiceover-tbc-wotlk). Please raise an issue if you have any comments or questions. Thanks!

## Using the project files

1. Clone the repo
2. Change the `docker-compose.yml` mounts for `AI_VoiceOverData_TBC`,`AI_VoiceOverData_WoTLK`, `AI_VoiceOverData_VanillaExtra` (lines 30-32) to wherever you want the audios to come out. Otherwise docker will make these folders next to your project folder. If you don't mind having the final audios stay in the container and then manually downloading them, you can delete these lines.
3. Start the docker container: `docker compose up -d`

This project uses XTTS and RVC to generate the quest and gossip audio. Starting up the container will trigger `download_models.sh`. This will create a folder structure called inputs inside the project directory and download the weights needed to get the Gradio WebUI up and running.

At this point, you can use the WebUI to initialize the database and prepare the data frame with the quest and gossip data. To start generating audio you need to provide some inputs:

* Reference audios in wav format. In project versions after 1.0.0, I modified the code to have XTTS accept multiple audio files to possibly improve audio quality. As a result, you need to organize your reference audios inside `inputs/voices` within folders with the voice_name values in the dataframe as the names of these folders. The audios for each voice_name go in here. You can further organize the audios into subfolders to channel specific emotions like sadness into audio generation. I provide an example of how this folder structure looks for me:
```
wow_vo_webui/
    └── inputs/
        └── voices/
            └── human_male/
                ├── default1.wav
                ├── default2.wav
                ├── sad/
                │   ├── sad1.wav
                │   └── sad2.wav
                └── angry/
                    ├── angry1.wav
                    └── angry2.wav
```
 You can specify what folder the model should look for audios in using the Emotion tab in the WebUI, and you can add or remove folder names by editing `wow_vo.py`, in the choices values for emotion_single and emotion_gossip. If you don't want to use any emotions you can leave all reference audios you want under the voice_name value folder (in the example, under human_male). 
* RVC weights (inside `inputs/fine_tuned/_rvc/weights`). The audio files must match the race_gender combination of the voice_name column in the dataframe (e.g., human_male.pth)
* RVC indices (inside `inputs/fine_tuned/_rvc/indices`). The audio files must match the race_gender combination of the voice_name column in the dataframe (e.g., human_male.index)
* XTTS fine-tuned models (inside `inputs/fine_tuned`). You must make a folder named with the value of voice_name that matches the character you want to voice, e.g., human_male. Inside you need to put the fine-tuned weights (called model.pth).
    * Fine-tuning XTTS is not necessary to get nice-sounding audio, but it provides a bit of pronunciation that can be nice depending on the data you train it on.
