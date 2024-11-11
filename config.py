# config.py

import os

llm_configs = {
    # Mistral Models
    "mistral-large-latest": {
        "base_url": "https://api.mistral.ai/v1",
        "api_key": os.environ.get("MISTRAL_API_KEY"),
        "provider": "mistral",
        "version": "mistral-large-2407"
    },
    "mistral-small-latest": {
        "base_url": "https://api.mistral.ai/v1", 
        "api_key": os.environ.get("MISTRAL_API_KEY"),
        "provider": "mistral",
        "version": "mistral-small-2409"
    },
    "open-mistral-nemo": {
        "base_url": "https://api.mistral.ai/v1",
        "api_key": os.environ.get("MISTRAL_API_KEY"), 
        "provider": "mistral",
        "version": "open-mistral-nemo-2407"
    },

    # Groq Models
    "llama-3.1-70b-versatile": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": os.environ.get("GROQ_API_KEY"),
        "provider": "groq"
    },
    "mixtral-8x7b-32768": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": os.environ.get("GROQ_API_KEY"),
        "provider": "groq"
    },
    "llama3-70b-8192": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key": os.environ.get("GROQ_API_KEY"),
        "provider": "groq"
    },

    # Grok Models  
    "grok-beta": {
        "base_url": "https://api.x.ai/v1",
        "api_key": os.environ.get("GROK_API_KEY"),
        "provider": "grok",
        "context_window": 131072,
        "pricing": {
            "input": 5,     # per 131,072 tokens
            "output": 15    # per 131,072 tokens
        }
    }
}
