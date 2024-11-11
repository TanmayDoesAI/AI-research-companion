# classes/transcript_processor.py

import os
import openai
import pickle
import re

from prompts import TRANSCRIPT_PROMPT, REWRITE_PROMPT
from config import llm_configs

class TranscriptProcessor:
    """
    A class to generate and rewrite podcast-style transcripts using a specified language model.
    """

    def __init__(self, text_file_path, transcript_output_path, tts_output_path, model_name="llama3-70b-8192", llm_config=None):
        """
        Initialize with the path to the cleaned text file and the model name.
        
        Args:
            text_file_path (str): Path to the file containing cleaned PDF text.
            transcript_output_path (str): Path to save the generated transcript.
            tts_output_path (str): Path to save the rewritten transcript for TTS.
            model_name (str): Name of the language model to use.
            llm_config (dict): Configuration for the LLM.
        """
        self.text_file_path = text_file_path
        self.transcript_output_path = transcript_output_path
        self.tts_output_path = tts_output_path
        self.model_name = model_name
        self.llm_config = llm_config or llm_configs.get(model_name)

        if self.llm_config is None:
            raise ValueError(f"Model configuration for {model_name} not found in llm_configs.")

        self.transcript_prompt = TRANSCRIPT_PROMPT
        self.rewrite_prompt = REWRITE_PROMPT

    def create_client(self):
        openai.api_key = self.llm_config["api_key"]
        openai.api_base = self.llm_config["base_url"]
        return openai

    def load_text(self):
        """
        Reads the cleaned text file and returns its content.
        
        Returns:
            str: Content of the cleaned text file.
        """
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        for encoding in encodings:
            try:
                with open(self.text_file_path, 'r', encoding=encoding) as file:
                    content = file.read()
                print(f"Successfully read file using {encoding} encoding.")
                return content
            except (UnicodeDecodeError, FileNotFoundError):
                continue
        print(f"Error: Could not decode file '{self.text_file_path}' with any common encoding.")
        return None

    def generate_transcript(self):
        """
        Generates a podcast-style transcript and saves it as a pickled file.
        
        Returns:
            str: Path to the file where the transcript is saved.
        """
        input_text = self.load_text()
        if input_text is None:
            return None
        
        messages = [
            {"role": "system", "content": self.transcript_prompt},
            {"role": "user", "content": input_text}
        ]
        
        client = self.create_client()

        response = client.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
        )

        transcript = response.choices[0].message.content

        # Save the transcript as a pickle file
        with open(self.transcript_output_path, 'wb') as f:
            pickle.dump(transcript, f)
        
        return self.transcript_output_path
        
    def extract_tuple(self, text):
        match = re.search(r'\[.*\]', text, re.DOTALL) 
        if match:
            return match.group(0)
        return None

    def rewrite_transcript(self):
        """
        Refines the transcript for TTS, adding expressive elements and saving as a list of tuples.
        
        Returns:
            str: Path to the file where the TTS-ready transcript is saved.
        """
        # Load the initial generated transcript
        with open(self.transcript_output_path, 'rb') as file:
            input_transcript = pickle.load(file)
        
        messages = [
            {"role": "system", "content": self.rewrite_prompt},
            {"role": "user", "content": input_transcript}
        ]
        
        client = self.create_client()

        response = client.ChatCompletion.create(
            model=self.model_name,
            messages=messages,
        )
        
        rewritten_transcript = self.extract_tuple(response.choices[0].message.content)
        
        # Save the rewritten transcript as a pickle file
        with open(self.tts_output_path, 'wb') as f:
            pickle.dump(rewritten_transcript, f)
        
        return self.tts_output_path
