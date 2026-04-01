import openai
import requests
import numpy as np

# Function to generate embeddings using OpenAI models

def generate_openai_embedding(text: str, model: str = 'text-embedding-ada-002') -> list:
    response = openai.Embedding.create(
        input=text,
        model=model
    )
    return response['data'][0]['embedding']

# Function to generate embeddings using Hugging Face models

def generate_huggingface_embedding(text: str, model: str):
    headers = {
        'Authorization': 'Bearer YOUR_HUGGINGFACE_API_TOKEN'
    }
    payload = {
        'inputs': text
    }
    response = requests.post(f'https://api-inference.huggingface.co/models/{model}', headers=headers, json=payload)
    return response.json()[0]['embedding']

# Function to generate embeddings using Ollama models

def generate_ollama_embedding(text: str, model: str) -> list:
    response = requests.post(f'http://localhost:11434/v1/models/{model}/generate', json={'input': text})
    return response.json()['data'][0]['embedding']
