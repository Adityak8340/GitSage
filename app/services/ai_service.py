from groq import Groq
from typing import Optional
from ..config import Config

class ChatResponse:
    def __init__(self):
        self.content = ""

    def add_chunk(self, text):
        self.content += text

    def get_content(self):
        return self.content

# Initialize Groq client
client = Groq(api_key=Config.GROQ_API_KEY)

async def get_code_explanation(code: str, path: str) -> str:
    """Get AI explanation for code"""
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert code reviewer and technical writer."
                },
                {
                    "role": "user",
                    "content": f"Please explain this code from {path}:\n\n{code}"
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error analyzing code: {str(e)}"

async def chat_with_repo(query: str, code_context: str = "", file_path: str = "") -> str:
    """Chat about repository code"""
    try:
        # Create a focused prompt
        prompt = f"""Context: Looking at file {file_path}

Code:
{code_context}

Question: {query}

Please provide a clear and specific answer based on the code shown above."""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful programming assistant. Focus on explaining code clearly and precisely."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"