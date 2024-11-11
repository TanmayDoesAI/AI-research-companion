# classes/pdf_text_extractor.py

import os
import openai
from PyPDF2 import PdfReader
import re
from tqdm import tqdm

from prompts import PDF_SYSTEM_PROMPT
from config import llm_configs
import time

class PDFTextExtractor:
    """
    A class to handle PDF text extraction and preprocessing for podcast preparation.
    """
    def __init__(self, pdf_path, output_path, model_name="llama3-8b-8192", llm_config=None, max_chars=100000, chunk_size=1000):
        """
        Initialize the PDFTextExtractor with paths and model details.
        
        Args:
            pdf_path (str): Path to the PDF file.
            output_path (str): Path to save the cleaned text file.
            model_name (str): Name of the model to use for text processing.
            llm_config (dict): Configuration for the LLM.
            max_chars (int): Maximum number of characters to process from the PDF.
            chunk_size (int): Size of text chunks to process at a time.
        """
        self.pdf_path = pdf_path
        self.output_path = output_path
        self.max_chars = max_chars
        self.chunk_size = chunk_size
        self.model_name = model_name
        self.llm_config = llm_config or llm_configs.get(model_name)
        
        if self.llm_config is None:
            raise ValueError(f"Model configuration for {model_name} not found in llm_configs.")
        
        # System prompt for text processing
        self.system_prompt = PDF_SYSTEM_PROMPT
    
    def create_client(self):
        openai.api_key = self.llm_config["api_key"]
        openai.api_base = self.llm_config["base_url"]
        return openai
    
    def validate_pdf(self):
        """Check if the file exists and is a valid PDF."""
        if not os.path.exists(self.pdf_path):
            print(f"Error: File not found at path: {self.pdf_path}")
            return False
        if not self.pdf_path.lower().endswith('.pdf'):
            print("Error: File is not a PDF")
            return False
        return True

    def extract_text(self):
        """Extract text from the PDF, limited by max_chars."""
        if not self.validate_pdf():
            return None
        
        with open(self.pdf_path, 'rb') as file:
            pdf_reader = PdfReader(file)
            num_pages = len(pdf_reader.pages)
            print(f"Processing PDF with {num_pages} pages...")
            
            extracted_text = []
            total_chars = 0
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text() or ""
                
                if total_chars + len(text) > self.max_chars:
                    remaining_chars = self.max_chars - total_chars
                    extracted_text.append(text[:remaining_chars])
                    print(f"Reached {self.max_chars} character limit at page {page_num + 1}")
                    break
                
                extracted_text.append(text)
                total_chars += len(text)
                print(f"Processed page {page_num + 1}/{num_pages}")
            
            final_text = '\n'.join(extracted_text)
            print(f"Extraction complete! Total characters: {len(final_text)}")
            return final_text

    def create_word_bounded_chunks(self, text):
        """Split text into chunks around the target size."""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            word_length = len(word) + 1  # +1 for the space
            if current_length + word_length > self.chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_length = word_length
            else:
                current_chunk.append(word)
                current_length += word_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def process_chunk(self, text_chunk):
        """Process a text chunk with the model and return the cleaned text."""
        conversation = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": text_chunk}
        ]
        client = self.create_client()

        response = client.ChatCompletion.create(
            model=self.model_name,
            messages=conversation,
        )
        
        processed_text = response.choices[0].message.content
        
        return processed_text

    def clean_and_save_text(self):
        """Extract, clean, and save processed text to a file."""
        extracted_text = self.extract_text()
        if not extracted_text:
            return None
        
        chunks = self.create_word_bounded_chunks(extracted_text)
        processed_text = ""
        
        with open(self.output_path, 'w', encoding='utf-8') as out_file:
            for chunk_num, chunk in enumerate(tqdm(chunks, desc="Processing chunks")):
                processed_chunk = self.process_chunk(chunk)
                processed_text += processed_chunk + "\n"
                out_file.write(processed_chunk + "\n")
                out_file.flush()
                time.sleep(3)  # To avoid rate limiting
        
        print(f"\nExtracted and cleaned text has been saved to {self.output_path}")
        return self.output_path
