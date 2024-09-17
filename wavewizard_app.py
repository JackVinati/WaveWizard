# app.py
import gradio as gr
from audio_analysis.audio_analysis import analyze_audio_files


def analyze_wrapper(files, folder_path):
    outputs = analyze_audio_files(files, folder_path)
    return outputs


with gr.Blocks() as demo:
    gr.Markdown("Wave Wizard")
    gr.Markdown(
        "Upload one or more audio files, or specify a folder containing audio files.")
    with gr.Row():
        file_input = gr.Files(label="Upload Audio Files",
                              type="filepath", file_count="multiple")
        folder_input = gr.Textbox(label="Folder Path (optional)",
                                  placeholder="Enter folder path containing audio files")
    analyze_button = gr.Button("Analyze")
    output_display = gr.HTML()

    # Bind the Gradio button to the analyze_wrapper function
    analyze_button.click(analyze_wrapper, inputs=[
                         file_input, folder_input], outputs=output_display)

demo.launch()
