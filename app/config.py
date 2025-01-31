import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev'
    GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
    GROQ_API_KEY = os.environ.get('GROQ_API_KEY')