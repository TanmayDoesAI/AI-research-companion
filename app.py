#main.py

import gradio as gr
import os
import shutil
import asyncio
import tempfile
import pickle
import traceback  # Import traceback for detailed error messages

from classes.pdf_text_extractor import PDFTextExtractor
from classes.transcript_processor import TranscriptProcessor
from classes.edge_tts_generator import EdgeTTSGenerator

from config import llm_configs

def create_temp_session_directory():
    return tempfile.mkdtemp()

def process_pdf_to_podcast(pdf_file, model_name, max_chars=100000, chunk_size=1000):
    try:
        session_dir = create_temp_session_directory()
        
        pdf_path = os.path.join(session_dir, "uploaded_pdf.pdf")
        clean_text_path = os.path.join(session_dir, "clean_text.txt")
        transcript_path = os.path.join(session_dir, "data.pkl")
        tts_ready_path = os.path.join(session_dir, "podcast_ready_data.pkl")
        audio_output_path = os.path.join(session_dir, "final_podcast_audio.mp3")
        
        shutil.copy(pdf_file.name, pdf_path)
        
        llm_config = llm_configs.get(model_name)
        if llm_config is None:
            return f"Model {model_name} not found in configuration.", None, None, None, None

        extractor = PDFTextExtractor(pdf_path, clean_text_path, model_name=model_name, llm_config=llm_config, max_chars=max_chars, chunk_size=chunk_size)
        clean_text_path = extractor.clean_and_save_text()
        
        with open(clean_text_path, 'r', encoding='utf-8') as file:
            text_preview = file.read(500)
        
        processor = TranscriptProcessor(clean_text_path, transcript_path, tts_ready_path, model_name=model_name, llm_config=llm_config)
        transcript_path = processor.generate_transcript()
        
        with open(transcript_path, 'rb') as f:
            transcript_preview = pickle.load(f)
        
        tts_ready_path = processor.rewrite_transcript()
        
        with open(tts_ready_path, 'rb') as f:
            tts_ready_preview = pickle.load(f)
        
        return (
            "Steps 1-3 completed successfully. Preview and adjust the rewritten transcript if needed.", 
            text_preview,
            transcript_preview,
            tts_ready_preview,
            session_dir 
        )
    except Exception as e:
        error_message = f"An error occurred during processing: {str(e)}"
        # Optionally, include traceback for debugging (comment out in production)
        # error_message += "\n" + traceback.format_exc()
        return error_message, None, None, None, None

def generate_audio_from_modified_text(tts_ready_text, session_dir):
    try:
        if not session_dir:
            session_dir = create_temp_session_directory()
        
        tts_ready_path = os.path.join(session_dir, "podcast_ready_data.pkl")
        audio_output_path = os.path.join(session_dir, "final_podcast_audio.mp3")
        
        with open(tts_ready_path, 'wb') as f:
            pickle.dump(tts_ready_text, f)
        
        tts_gen = EdgeTTSGenerator(tts_ready_path, audio_output_path)
        audio_path = asyncio.run(tts_gen.generate_audio())
        return "Step 4 completed successfully. Audio saved.", audio_path
    except Exception as e:
        error_message = f"An error occurred during audio generation: {str(e)}"
        # Optionally, include traceback for debugging (comment out in production)
        # error_message += "\n" + traceback.format_exc()
        return error_message, None

# Gradio Interface with Informative Descriptions and Multi-page Layout
custom_theme = gr.themes.Default(
    primary_hue="purple",
    secondary_hue="purple",
).set(
    button_primary_background_fill="#6A0DAD",  # Deep purple for primary button
    button_primary_background_fill_hover="#8B5FBF",  # Lighter purple on hover
    button_primary_border_color="#6A0DAD",  # Deep purple for border color
    button_primary_border_color_hover="#8B5FBF",  # Lighter purple on hover
    checkbox_background_color="#4B0082",  # Indigo for checkboxes
    checkbox_background_color_hover="#7D3F98",  # Slightly lighter purple on hover
)

with gr.Blocks(theme=custom_theme) as app:
    gr.Markdown("# AI Research Companion - Transforming Papers into Podcasts")
    gr.Markdown("Harnessing AI to make research more accessible and effortless, by converting complex papers into engaging audio experiences.")
    # Page 1: Project Overview and PDF Upload
    with gr.Tab("Overview and Upload"):
        gr.Markdown("""

        ## Project Background
        This project started during the Smart India Hackathon (SIH) as a solution to a challenge I personally faced—keeping up with the overwhelming influx of research papers. Realizing how intense and time-consuming this was, I thought an AI-driven tool could make academic content more accessible. By leveraging large language models, this tool converts dense research into easily understandable audio, offering an easier way for everyone to engage with academic material.

        Development is ongoing, with future plans to add web search and additional TTS options for a richer experience. Special thanks to  [yasserrmd](https://huggingface.co/spaces/yasserrmd/NotebookLlama) inspiring the structured prompts behind this project.
                    
        This AI Research Companion bridges the gap between research and accessibility, transforming detailed papers into podcasts for more convenient, on-the-go learning. Just upload a PDF to start the conversion.
        """)
        
        with gr.Row():
            pdf_input = gr.File(label="Upload PDF", type='filepath')
            text_model = gr.Dropdown(
                label="Select Text Model",
                choices=list(llm_configs.keys()),
                value="llama3-70b-8192"
            )
            max_chars = gr.Number(label="Max Characters to Process", value=100000, maximum=100000)
            chunk_size = gr.Number(label="Chunk Size", value=1000)
            run_all_button = gr.Button("Process Document")
            output_status = gr.Textbox(label="Status", interactive=False, lines=5)
    # Page 2: Preview Extracted Text
    with gr.Tab("Text Extraction"):
        gr.Markdown("""
        ## Text Extraction
        At this stage, your research paper’s content is carefully extracted, setting the foundation for its transformation into an audio-friendly format.
        This extracted text will be used to generate a transcript and prepare it for text-to-speech (TTS) conversion.
        """)
        extracted_text_preview = gr.Textbox(label="Extracted Text Preview (First 500 Characters)", interactive=False, lines=10)
    # Page 3: Generate Transcript
    with gr.Tab("Transcript Generation"):
        gr.Markdown("""
        ## Transcript Generation
        Here, the extracted text is structured into a clean, readable transcript, perfect for creating clear audio and adjusting any finer details.
        This transcript can be modified before proceeding to the next step for audio generation. And fix any other errors left by the large language model.
        """)
        transcript_preview = gr.Textbox(label="Generated Transcript Preview", interactive=False, lines=10)
    # Page 4: Edit TTS-ready Transcript
    with gr.Tab("Edit Transcript for TTS"):
        gr.Markdown("""
        ## Edit Transcript for TTS
       This refined transcript is ready for a final polish, ensuring it’s clear and precise before creating an audio experience.
        Users can make final adjustments to the text here to ensure accuracy and coherence before audio generation.
        """)
        tts_ready_preview = gr.Textbox(label="Editable Rewritten Transcript for TTS", interactive=True, lines=10)
        generate_audio_button = gr.Button("Generate Audio from Edited Transcript")
    # Page 5: Listen to Generated Podcast Audio
    with gr.Tab("Audio Output"):
        gr.Markdown("""
        ## Audio Output
       Your transformed audio is now ready! Listen to your research in a podcast-like format, perfect for accessible and engaging learning on-the-go.
        """)
        final_audio_output = gr.Audio(label="Generated Podcast Audio")
    
    session_dir = gr.State()
    # Execute Steps 1-3: Upload, Process, Extract
    run_all_button.click(
        process_pdf_to_podcast, 
        inputs=[pdf_input, text_model, max_chars, chunk_size], 
        outputs=[output_status, extracted_text_preview, transcript_preview, tts_ready_preview, session_dir]
    )
    # Step 4: Generate Audio from Edited Transcript
    generate_audio_button.click(
        generate_audio_from_modified_text, 
        inputs=[tts_ready_preview, session_dir],
        outputs=[output_status, final_audio_output]
    )

app.launch()
