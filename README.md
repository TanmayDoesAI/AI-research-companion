# AI Research Companion - Transforming Research Papers into Podcasts

## Overview
The AI Research Companion is an innovative tool designed to make academic research more accessible. It transforms complex, text-heavy research papers into audio podcasts, enabling users to consume academic content in a more engaging and convenient way.

This project was initially developed during the Smart India Hackathon (SIH) in 2023 to address the overwhelming challenge of managing and understanding a large number of research papers. It leverages large language models (LLMs) to extract relevant text, generate readable transcripts, and convert these into audio podcasts.

## Features
- **Text Extraction:** Extracts content from uploaded PDFs to create clean, readable text.
- **Transcript Generation:** Uses AI to generate a coherent transcript from the extracted text.
- **TTS (Text-to-Speech):** Converts the refined transcript into an audio file.
- **Editable Transcript:** Users can modify the transcript before converting it into audio, allowing for better control over the final output.
- **Audio Output:** Listen to the final generated podcast from the research paper.

## Development Status
The tool is still under development with plans to:
- Integrate web search capabilities to find related research.
- Explore additional Text-to-Speech engines to enhance the audio output.

## Requirements
- Python 3.7 or higher
- Gradio
- Various AI/LLM APIs (configured in the `config` directory)
- Edge TTS for audio generation

## Setup Instructions
1. Clone this repository to your local machine:
    ```bash
    git clone <repository_url>
    ```
2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3. Set up API keys for the LLM models in the `config` directory.

## Usage
1. **Upload PDF:** Start by uploading a research paper in PDF format.
2. **Select Model:** Choose the text model for processing the document.
3. **Text Preview:** Preview the extracted text before proceeding.
4. **Transcript Preview:** Review the generated transcript and make edits if needed.
5. **TTS Output:** After finalizing the transcript, generate the audio podcast from the text.

## Note:
This tool uses APIs for LLMs, but if GPUs are available, you can easily switch the API base to local models like "ollama" for enhanced performance.

## Acknowledgements
Special thanks to [yasserrmd](https://huggingface.co/spaces/yasserrmd/NotebookLlama) for inspiring the structured prompts that guide this project.

## License
This project is open source under the MIT License. Feel free to contribute and improve the tool.
