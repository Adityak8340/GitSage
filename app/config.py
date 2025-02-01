import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    if not GITHUB_TOKEN:
        raise ValueError("GitHub token not found! Please set GITHUB_TOKEN environment variable.")
    if not GROQ_API_KEY:
        raise ValueError("Groq API key not found! Please set GROQ_API_KEY environment variable.")