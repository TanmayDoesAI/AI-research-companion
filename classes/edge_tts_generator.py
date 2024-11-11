# classes/edge_tts_generator.py

import asyncio
import pickle
import re
from tqdm import tqdm
import ast
import edge_tts

class EdgeTTSGenerator:
    """
    A class to generate podcast-style audio from a transcript using edge-tts.
    """
    def __init__(self, transcript_file_path, output_audio_path):
        """
        Initialize the TTS generator with the path to the rewritten transcript file.
        
        Args:
            transcript_file_path (str): Path to the file containing the rewritten transcript.
            output_audio_path (str): Path to save the generated audio file.
        """
        self.transcript_file_path = transcript_file_path
        self.output_audio_path = output_audio_path

        # Speaker descriptions for edge-tts voices
        self.speaker1_voice = "en-US-AriaNeural"
        self.speaker2_voice = "en-US-GuyNeural"

    def load_transcript(self):
        """
        Loads the rewritten transcript from the specified file.
        
        Returns:
            list: The content of the transcript as a list of tuples (speaker, text).
        """
        with open(self.transcript_file_path, 'rb') as f:
            return ast.literal_eval(pickle.load(f))

    async def generate_audio_segment(self, text, voice_name):
        """
        Generate audio for a given text using edge-tts.
        
        Args:
            text (str): Text to be synthesized.
            voice_name (str): The voice name to use for TTS.
        
        Returns:
            bytes: Generated audio data.
        """
        communicator = edge_tts.Communicate(text, voice_name)
        audio_bytes = b""
        async for chunk in communicator.stream():
            if "data" in chunk:  # Check if 'data' exists in chunk
                audio_bytes += chunk["data"]  # Concatenate only the audio data
        return audio_bytes

    def save_audio(self, audio_data):
        """
        Save the combined audio data to an output file.
        
        Args:
            audio_data (list): List of bytes containing the audio data for each segment.
        """
        combined_audio = b"".join(audio_data)
        with open(self.output_audio_path, "wb") as f:
            f.write(combined_audio)

    async def generate_audio(self):
        """
        Converts the transcript into audio and saves it to a file.
        
        Returns:
            str: Path to the saved audio file.
        """
        transcript = self.load_transcript()
        audio_data = []

        for speaker, text in tqdm(transcript, desc="Generating podcast segments", unit="segment"):
            voice = self.speaker1_voice if speaker == "Speaker 1" else self.speaker2_voice
            segment_audio = await self.generate_audio_segment(text, voice)
            audio_data.append(segment_audio)

        self.save_audio(audio_data)
        return self.output_audio_path
