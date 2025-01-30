from flask import current_app
from groq import Groq
import json

class ChatResponse:
    def __init__(self):
        self.content = ""

    def add_chunk(self, text):
        self.content += text

    def get_content(self):
        return self.content

def get_groq_client():
    """Initialize Groq client with API key"""
    return Groq(api_key=current_app.config['GROQ_API_KEY'])

def get_code_explanation(code, file_path):
    """Explain code using Groq AI"""
    client = get_groq_client()
    response = ChatResponse()
    
    prompt = f"""Analyze this code from {file_path} and explain:
    1. What it does
    2. Key components and functions
    3. Potential improvements

    Code:
    {code}
    """
    
    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert code reviewer and technical writer.",
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            temperature=0.7,
            max_completion_tokens=1024,
            stream=True
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                response.add_chunk(chunk.choices[0].delta.content)

        return response.get_content()
    except Exception as e:
        return f"Error analyzing code: {str(e)}"

def chat_with_repo(query, code_context="", file_path=""):
    """Chat about repository code using Groq AI"""
    client = get_groq_client()
    response = ChatResponse()
    
    # Prepare a more detailed system prompt
    system_prompt = """You are a helpful AI assistant specializing in code analysis and explanation.
    When asked about specific functions or features:
    1. If the function exists in the provided code context, explain it in detail
    2. If the function doesn't exist, clearly state that it's not found in the current code
    3. Always refer to the actual code content when explaining
    4. If there's an error or limitation, explain it clearly
    """
    
    # Build user prompt with context
    user_prompt = f"""Context: I'm looking at the file {file_path}
    
    Code content:
    {code_context}
    
    Question: {query}
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            temperature=0.7,
            max_completion_tokens=1024,
            stream=True
        )

        for chunk in completion:
            if chunk.choices[0].delta.content:
                response.add_chunk(chunk.choices[0].delta.content)

        # If no content was found, provide a clear error message
        if not response.content.strip():
            return "I couldn't find any information about that in the current code. Please make sure you have a file selected and try asking about functions or features that exist in the code."

        return response.get_content()
    except Exception as e:
        return f"""I encountered an error while processing your question. Here's what you can try:
        1. Make sure you have a file selected
        2. Check if the function or feature you're asking about exists in the current file
        3. Try rephrasing your question
        
        Error details: {str(e)}"""