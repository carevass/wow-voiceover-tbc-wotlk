from wowvo_client.tts_utils import TTSProcessor
from clean_data import clean_quest_data
from data_prep.init_db import init_db
import os
import sys
import gradio as gr

now_dir = os.getcwd()
sys.path.append(now_dir)
os.makedirs(os.path.join(now_dir, "webui_output"), exist_ok=True)

tts_processor = TTSProcessor()

f0_up_key = 0

selected_voice_names = []

def load_voices(df):
    selected_voice_names = df['voice_name'].drop_duplicates().tolist()
    return gr.CheckboxGroup(choices=selected_voice_names, value=selected_voice_names)

def select_columns(df):
    return df[['source', 'quest', 'quest_title', 'name','id','voice_name','DisplayRaceID', 'DisplaySexID','cleanedText', 'expansion']]

with gr.Blocks(title="WoW Voiceover WebUI", theme = gr.themes.Ocean()) as app:
    df_state = gr.State(value=None)
    gr.Markdown("## WoW Voiceover WebUI")
    gr.Markdown(
        value = "Voiceover for quests and gossip from WoW, configured for TBC and WoTLK."

    )
    with gr.Tabs():
        with gr.TabItem("Data preparation"):
            with gr.Group():
                with gr.Row():
                    but0 = gr.Button("Initialize Database", variant="primary")
                    info0 = gr.Textbox(label="Output", value="")
                    but0.click(
                        init_db,
                        inputs=[],
                        outputs=info0,
                    )
            with gr.Group():
                with gr.Row():
                    but1 = gr.Button("Create gossip & quest data", variant="primary")
                    info1 = gr.Textbox(label="Output", value="")
                    but1.click(
                        lambda: clean_quest_data(tts_processor),
                        inputs=[],
                        outputs=[info1,df_state],
                    )
            with gr.Group():
                with gr.Row():
                        dataframe_display = gr.Dataframe(
                            show_search = 'search',
                            wrap = True
                            #column_widths = ["",'75px','','','75px']
                        )
            df_state.change(
                select_columns,
                inputs=[df_state],
                outputs=[dataframe_display]
            )


        with gr.TabItem("TTS by quest"):
            with gr.Group():
                with gr.Row():
                    with gr.Column():
                        xtts_param_label = gr.Markdown("XTTS Parameters")
                        temperature_single = gr.Slider(
                            minimum=0,
                            maximum=1,
                            label="Temperature",
                            value=0.75,
                            interactive=True,
                        )
                        length_penalty_single = gr.Slider(
                            minimum=-10,
                            maximum=10,
                            label="Length penalty",
                            value=1,
                            interactive=True,
                        )
                        repetition_penalty_single = gr.Slider(
                            minimum=0,
                            maximum=15,
                            label="Repetition penalty",
                            value=10,
                            step = 0.5,
                            interactive=True,
                        )
                        top_k_single = gr.Slider(
                            minimum=1,
                            maximum=100,
                            label="Top k",
                            value=1,
                            step = 1,
                            interactive=True,
                        )
                        top_p_single = gr.Slider(
                            minimum=0,
                            maximum=1,
                            label="Top p",
                            value=1.0,
                            interactive=True,
                        )
                        speed_single = gr.Slider(
                            minimum=0.01,
                            maximum=2,
                            label="Speed",
                            value=1.05,
                            interactive=True,
                        )
                    with gr.Column():
                        rvc_param_label = gr.Markdown("RVC Parameters")
                        with gr.Row():
                            f0_method_single = gr.Radio(
                                    label=" Select the pitch extraction algorithm",
                                    choices=(
                                        ["pm", "harvest", "crepe", "rmvpe"]
                                    ),
                                    value = "rmvpe"
                                )
                        f0_up_key_single = gr.Textbox(
                            value = 0,
                            visible = False
                        )
                        index_rate_single = gr.Slider(
                            minimum=0,
                            maximum=1,
                            label="Index rate to control accent strength",
                            value=0.75,
                            interactive=True,
                        )
                        filter_radius_single = gr.Slider(
                            minimum=0,
                            maximum=7,
                            label="Apply median filter to harvested pitch results",
                            value=3,
                            step=1,
                            interactive=True,
                        )
                        resample_sr_single = gr.Slider(
                            minimum=0,
                            maximum=48000,
                            label="Target resample rate after processing, set to 0 for no resampling",
                            value=0,
                            step=1,
                            interactive=True,
                        )
                        rms_mix_rate_single = gr.Slider(
                            minimum=0,
                            maximum=1,
                            label="Adjust the volume envelope scaling.",
                            value=0.25,
                            interactive=True,
                        )
                        protect_single = gr.Slider(
                            minimum=0,
                            maximum=0.5,
                            label="Protect rate",
                            value=0.25,
                            step=0.01,
                            interactive=True,
                        )
            with gr.Group():
                with gr.Row():
                    with gr.Column():
                        expansion_label = gr.Markdown("Choose whether you are generating the accept, complete or both parts of the quest audio")
                        spec_single = gr.Dropdown(
                            label="",
                            choices=(
                                ['accept','complete']
                            ),
                            value = ['accept','complete'],
                            multiselect = True,
                            interactive = True
                            )
                    with gr.Column():
                        module_label = gr.Markdown("Module to export audio to")
                        module_name_single = gr.Dropdown(
                            label="",
                            choices=(
                                ['AI_VoiceOverData_VanillaExtra', 'AI_VoiceOverData_TBC', 'AI_VoiceOverData_WoTLK','Testing']
                            ),
                            value = 'Testing',
                            allow_custom_value = True,
                            interactive = True
                            )
                    with gr.Column():
                        questid_label = gr.Markdown("Write the quest ID of the quest you will be regenerating")
                        quest_id = gr.Textbox(
                            interactive = True
                            )
            with gr.Group():
                with gr.Row():
                    expansions_state = gr.State()  # Hidden state to store expansions
                    audio_gr = gr.Audio(label="Synthesised Audio", interactive=False, autoplay=True)
                    but0 = gr.Button("Generate audio", variant="primary")
                    info0 = gr.Textbox(label="Output", value="")

                    but0.click(
                        tts_processor.tts_quest,
                        inputs=[
                            df_state,
                            quest_id,
                            module_name_single,
                            spec_single,
                            temperature_single,
                            length_penalty_single,
                            repetition_penalty_single,
                            top_k_single,
                            top_p_single,
                            speed_single,
                            f0_up_key_single,
                            f0_method_single,
                            index_rate_single,
                            filter_radius_single,
                            resample_sr_single,
                            rms_mix_rate_single,
                            protect_single

                        ],
                        outputs=[info0, expansions_state, audio_gr],
                    )
                    with gr.Row():
                        but1 = gr.Button("Generate lookup tables", variant="primary")
                        info1 = gr.Textbox(label="Output", value="")

                        but1.click(
                            tts_processor.generate_lookup_tables,
                            inputs=[
                                df_state,
                                expansions_state,
                                module_name_single,
                            ],
                            outputs=info1,
                        )
        with gr.TabItem("TTS Gossip"):
            with gr.Group():
                with gr.Row():
                    with gr.Column():
                        xtts_param_label = gr.Markdown("XTTS Parameters")
                        temperature_gossip = gr.Slider(
                            minimum=0,
                            maximum=1,
                            label="Temperature",
                            value=0.75,
                            interactive=True,
                        )
                        length_penalty_gossip = gr.Slider(
                            minimum=-10,
                            maximum=10,
                            label="Length penalty",
                            value=1,
                            interactive=True,
                        )
                        repetition_penalty_gossip = gr.Slider(
                            minimum=0,
                            maximum=15,
                            label="Repetition penalty",
                            value=10,
                            step = 0.5,
                            interactive=True,
                        )
                        top_k_gossip = gr.Slider(
                            minimum=1,
                            maximum=100,
                            label="Top k",
                            value=1,
                            step = 1,
                            interactive=True,
                        )
                        top_p_gossip = gr.Slider(
                            minimum=0,
                            maximum=1,
                            label="Top p",
                            value=1.0,
                            interactive=True,
                        )
                        speed_gossip = gr.Slider(
                            minimum=0.01,
                            maximum=2,
                            label="Speed",
                            value=1.05,
                            interactive=True,
                        )
                    with gr.Column():
                        rvc_param_label = gr.Markdown("RVC Parameters")
                        with gr.Row():
                            f0_method_gossip = gr.Radio(
                                    label=" Select the pitch extraction algorithm",
                                    choices=(
                                        ["pm", "harvest", "crepe", "rmvpe"]
                                    ),
                                    value = "rmvpe"
                                )
                        f0_up_key_gossip = gr.Textbox(
                            value = 0,
                            visible = False
                        )
                        index_rate_gossip = gr.Slider(
                            minimum=0,
                            maximum=1,
                            label="Index rate to control accent strength",
                            value=0.75,
                            interactive=True,
                        )
                        filter_radius_gossip = gr.Slider(
                            minimum=0,
                            maximum=7,
                            label="Apply median filter to harvested pitch results",
                            value=3,
                            step=1,
                            interactive=True,
                        )
                        resample_sr_gossip = gr.Slider(
                            minimum=0,
                            maximum=48000,
                            label="Target resample rate after processing, set to 0 for no resampling",
                            value=0,
                            step=1,
                            interactive=True,
                        )
                        rms_mix_rate_gossip = gr.Slider(
                            minimum=0,
                            maximum=1,
                            label="Adjust the volume envelope scaling.",
                            value=0.25,
                            interactive=True,
                        )
                        protect_gossip = gr.Slider(
                            minimum=0,
                            maximum=0.5,
                            label="Protect rate",
                            value=0.25,
                            step=0.01,
                            interactive=True,
                        )
            with gr.Group():
                with gr.Row():
                    with gr.Column():
                        module_label = gr.Markdown("Module to export audio to")
                        module_name_gossip = gr.Dropdown(
                            label="",
                            choices=(
                                ['AI_VoiceOverData_VanillaExtra', 'AI_VoiceOverData_TBC', 'AI_VoiceOverData_WoTLK','Testing']
                            ),
                            value = 'Testing',
                            allow_custom_value = True,
                            interactive = True
                            )
                    with gr.Column():
                        npc_label = gr.Markdown("Write the NPC name you will be regenerating audio for")
                        npc_name = gr.Textbox(
                            interactive = True
                            )
            with gr.Group():
                with gr.Row():
                    expansions_gossip = gr.State()  # Hidden state to store expansions
                    audio_gs = gr.Audio(label="Synthesised Audio", interactive=False, autoplay=True)
                    but2 = gr.Button("Generate audio", variant="primary")
                    info2 = gr.Textbox(label="Output", value="")

                    but2.click(
                        tts_processor.tts_gossip,
                        inputs=[
                            df_state,
                            module_name_gossip,
                            npc_name,
                            temperature_gossip,
                            length_penalty_gossip,
                            repetition_penalty_gossip,
                            top_k_gossip,
                            top_p_gossip,
                            speed_gossip,
                            f0_up_key_gossip,
                            f0_method_gossip,
                            index_rate_gossip,
                            filter_radius_gossip,
                            resample_sr_gossip,
                            rms_mix_rate_gossip,
                            protect_gossip

                        ],
                        outputs=[info2, expansions_gossip, audio_gs],
                    )
                    with gr.Row():
                        but3 = gr.Button("Generate lookup tables", variant="primary")
                        info3 = gr.Textbox(label="Output", value="")

                        but3.click(
                            tts_processor.generate_lookup_tables,
                            inputs=[
                                df_state,
                                expansions_gossip,
                                module_name_gossip,
                            ],
                            outputs=info3,
                        )
        with gr.TabItem("Batch TTS"):
            with gr.Group():
                with gr.Accordion("Select voices to produce audio on"):
                    load_voices_button = gr.Button("Load available voices", variant="primary")
                    selected_voice_names = gr.CheckboxGroup(
                            label="Choose all the voices that you want to generate audio for. By default, all voices are selected." ,
                            choices=[],
                            value = [],
                            show_label = True,
                            show_select_all = True,
                            interactive = True
                    )
                    load_voices_button.click(
                        load_voices,
                        inputs=[df_state],
                        outputs=selected_voice_names
                    )
            with gr.Group():
                with gr.Row():
                    with gr.Column():
                        xtts_param_label = gr.Markdown("XTTS Parameters")
                        temperature_batch = gr.Slider(
                            minimum=0,
                            maximum=1,
                            label="Temperature",
                            value=0.75,
                            interactive=True,
                        )
                        length_penalty_batch = gr.Slider(
                            minimum=-10,
                            maximum=10,
                            label="Length penalty",
                            value=1,
                            interactive=True,
                        )
                        repetition_penalty_batch = gr.Slider(
                            minimum=0,
                            maximum=15,
                            label="Repetition penalty",
                            value=10,
                            step =0.5,
                            interactive=True,
                        )
                        top_k_batch = gr.Slider(
                            minimum=1,
                            maximum=100,
                            label="Top k",
                            value=1,
                            step = 1,
                            interactive=True,
                        )
                        top_p_batch = gr.Slider(
                            minimum=0,
                            maximum=1,
                            label="Top p",
                            value=1.0,
                            interactive=True,
                        )
                        speed_batch = gr.Slider(
                            minimum=0.01,
                            maximum=2,
                            label="Speed",
                            value=1.05,
                            interactive=True,
                        )
                    with gr.Column():
                        rvc_param_label = gr.Markdown("RVC Parameters")
                        with gr.Row():
                            f0_method_batch = gr.Radio(
                                    label=" Select the pitch extraction algorithm",
                                    choices=(
                                        ["pm", "harvest", "crepe", "rmvpe"]
                                    ),
                                    value = "rmvpe"
                                )
                        f0_up_key_batch = gr.Textbox(
                            value = 0,
                            visible = False
                        )
                        index_rate_batch = gr.Slider(
                            minimum=0,
                            maximum=1,
                            label="Index rate to control accent strength",
                            value=0.75,
                            interactive=True,
                        )
                        filter_radius_batch = gr.Slider(
                            minimum=0,
                            maximum=7,
                            label="Apply median filter to harvested pitch results",
                            value=3,
                            step=1,
                            interactive=True,
                        )
                        resample_sr_batch = gr.Slider(
                            minimum=0,
                            maximum=48000,
                            label="Target resample rate after processing, set to 0 for no resampling",
                            value=0,
                            step=1,
                            interactive=True,
                        )
                        rms_mix_rate_batch = gr.Slider(
                            minimum=0,
                            maximum=1,
                            label="Adjust the volume envelope scaling.",
                            value=0.25,
                            interactive=True,
                        )
                        protect_batch = gr.Slider(
                            minimum=0,
                            maximum=0.5,
                            label="Protect rate",
                            value=0.25,
                            step=0.01,
                            interactive=True,
                        )
            with gr.Group():
                with gr.Row():
                    with gr.Column():
                        expansion_label = gr.Markdown("Choose Expansion(s) to produce audio for")
                        expansions = gr.Dropdown(
                            label="",
                            choices=(
                                ['Vanilla', 'TBC', 'WoTLK']
                            ),
                            value = ['Vanilla', 'TBC', 'WoTLK'],
                            type = 'index',
                            multiselect = True,
                            interactive = True
                            )
                    with gr.Column():
                        module_label = gr.Markdown("Module to export audio to")
                        module_name = gr.Dropdown(
                            label="",
                            choices=(
                                ['AI_VoiceOverData_VanillaExtra', 'AI_VoiceOverData_TBC', 'AI_VoiceOverData_WoTLK','Testing']
                            ),
                            value = 'Testing',
                            allow_custom_value = True,
                            interactive = True
                            )
            with gr.Group():
                with gr.Row():
                    but0 = gr.Button("Generate audio", variant="primary")
                    info0 = gr.Textbox(label="Output", value="")

                    but0.click(
                        tts_processor.tts_dataframe,
                        inputs=[
                            df_state,
                            selected_voice_names,
                            expansions,
                            module_name,
                            temperature_batch,
                            length_penalty_batch,
                            repetition_penalty_batch,
                            top_k_batch,
                            top_p_batch,
                            speed_batch,
                            f0_up_key_batch,
                            f0_method_batch,
                            index_rate_batch,
                            filter_radius_batch,
                            resample_sr_batch,
                            rms_mix_rate_batch,
                            protect_batch

                        ],
                        outputs=info0,
                    )
                    with gr.Row():
                        but1 = gr.Button("Generate lookup tables", variant="primary")
                        info1 = gr.Textbox(label="Output", value="")

                        but1.click(
                            tts_processor.generate_lookup_tables,
                            inputs=[
                                df_state,
                                expansions,
                                module_name,
                            ],
                            outputs=info1,
                        )
app.launch(
    server_name="0.0.0.0",
    server_port=7280
)
