# WoW Voiceover: TBC \& WoTLK

This is an unofficial expansion of [WoWVoiceOver](https://github.com/mrthinger/wow-voiceover). it includes:

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

* Reference audios in wav format (inside `inputs/voices`). The audio files must match the race_gender combination of the voice_name column in the dataframe (e.g., human_male.wav)
* RVC weights (inside `inputs/fine_tuned/_rvc/weights`). The audio files must match the race_gender combination of the voice_name column in the dataframe (e.g., human_male.pth)
* RVC indices (inside `inputs/fine_tuned/_rvc/indices`). The audio files must match the race_gender combination of the voice_name column in the dataframe (e.g., human_male.index)
* XTTS fine-tuned models (inside `inputs/fine_tuned`). You must make a folder named with the value of voice_name that matches the character you want to voice, e.g., human_male. Inside you need to put the fine-tuned weights (called model.pth).
    * Fine-tuning XTTS is not necessary to get nice-sounding audio, but it provides a bit of pronounciation that can be nice depending on the data you train it on.
