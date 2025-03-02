from groq import Groq
from typing import Optional, List, Dict, Any
from ..config import Config
import re

class ChatResponse:
    def __init__(self):
        self.content = ""
    
    def add_chunk(self, text):
        self.content += text
    
    def get_content(self):
        return self.content

def is_greeting_or_general(query: str) -> bool:
    greetings = ["hi", "hello", "hey", "greetings"]
    return any(query.lower().startswith(g) for g in greetings)

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

def truncate_large_text(content: str, file_path: str, max_chars: int = 10000) -> str:
    """
    Intelligently truncate large text files to prevent API token limit errors.
    This function handles different file types appropriately.
    """
    # Skip if content is small enough
    if len(content) <= max_chars:
        return content
    
    print(f"Truncating large file: {file_path} ({len(content)} chars)")
    
    # Check for binary file content (might be mistakenly treated as text)
    if _is_likely_binary(content):
        return f"[Binary file detected: {file_path} - {len(content)} bytes]"
    
    # Get file extension (without the dot) or empty string if no extension
    file_ext = file_path.split('.')[-1].lower() if '.' in file_path else ''
    
    # Handle different file types
    if file_ext in ['md', 'markdown']:
        # For markdown files, preserve headers and structure
        return _truncate_markdown(content, max_chars)
    elif file_ext in ['py', 'js', 'java', 'c', 'cpp', 'cs', 'go']:
        # For code files, preserve imports/includes and function signatures
        return _truncate_code(content, file_ext, max_chars)
    elif file_ext in ['json', 'yaml', 'yml', 'xml']:
        # For structured data files, preserve structure
        return _truncate_structured_data(content, file_ext, max_chars)
    elif file_ext in ['bpe', 'vocab', 'dict', 'txt', 'csv', 'tsv']:
        # For vocabulary/dictionary files, sample entries
        return _truncate_dictionary_file(content, max_chars)
    else:
        # Default truncation for unknown file types
        return _truncate_generic(content, max_chars)

def _is_likely_binary(content: str, sample_size: int = 1000) -> bool:
    """Check if content is likely binary data"""
    # Take a sample of the content to check
    sample = content[:sample_size]
    # Count non-printable/control characters
    control_char_count = sum(1 for c in sample if ord(c) < 32 and c not in '\n\r\t')
    # If more than 10% are control characters, it's likely binary
    return (control_char_count / len(sample)) > 0.10

def _truncate_markdown(content: str, max_chars: int) -> str:
    """Truncate markdown preserving structure"""
    lines = content.split('\n')
    
    # Extract all headers
    headers = [line for line in lines if line.strip().startswith('#')]
    
    # Take beginning and some end
    beginning = '\n'.join(lines[:max(10, max_chars//200)])
    
    # Build summary
    result = f"{beginning}\n\n...\n\n[Content truncated - file is {len(content)} characters]\n\n"
    
    if headers:
        result += "## Document Structure:\n"
        for h in headers[:20]:
            result += f"{h}\n"
        if len(headers) > 20:
            result += f"\n... and {len(headers) - 20} more headers\n"
    
    return result

def _truncate_code(content: str, ext: str, max_chars: int) -> str:
    """Truncate code files preserving imports and function definitions"""
    lines = content.split('\n')
    
    # Extract imports, class definitions, and function definitions
    imports = []
    definitions = []
    
    import_patterns = {
        'py': ['import ', 'from '],
        'js': ['import ', 'require(', 'from '],
        'java': ['import '],
        'c': ['#include'],
        'cpp': ['#include'],
        'cs': ['using '],
        'go': ['import ']
    }
    
    def_patterns = {
        'py': ['def ', 'class '],
        'js': ['function ', 'class ', 'const ', 'let ', 'var '],
        'java': ['class ', 'interface ', 'enum ', 'public ', 'private ', 'protected '],
        'c': [') {', ') \{'],
        'cpp': [') {', ') \{', 'class ', 'struct '],
        'cs': ['class ', 'void ', 'public ', 'private '],
        'go': ['func ', 'type ']
    }
    
    patterns = import_patterns.get(ext, [])
    for i, line in enumerate(lines):
        if any(line.strip().startswith(p) for p in patterns):
            imports.append((i, line))
    
    patterns = def_patterns.get(ext, [])
    for i, line in enumerate(lines):
        if any(p in line for p in patterns) and '{' in line or '):' in line:
            definitions.append((i, line))
    
    # Build a useful summary
    # First, add the first 20-30 lines, which often include imports and setup
    start_section = '\n'.join(lines[:min(30, len(lines)//10)])
    
    result = f"{start_section}\n\n...\n\n[Code file truncated - {len(content)} characters total]\n\n"
    
    # Add imports section if we found imports
    if imports:
        result += "## Imports/Includes:\n```\n"
        for _, line in imports[:20]:
            result += f"{line}\n"
        if len(imports) > 20:
            result += f"# ... and {len(imports) - 20} more imports\n"
        result += "```\n\n"
    
    # Add function/class definitions
    if definitions:
        result += "## Function/Class Definitions:\n```\n"
        for _, line in definitions[:30]:
            result += f"{line}\n"
        if len(definitions) > 30:
            result += f"# ... and {len(definitions) - 30} more definitions\n"
        result += "```\n"
    
    return result

def _truncate_structured_data(content: str, ext: str, max_chars: int) -> str:
    """Truncate structured data files (JSON, YAML, XML)"""
    lines = content.split('\n')
    
    # Take some from beginning and some from end
    beginning = '\n'.join(lines[:max(15, max_chars//200)])
    
    # Build summary
    result = f"{beginning}\n\n...\n\n[Content truncated - file is {len(content)} characters]\n\n"
    
    # Try to extract structure based on file type
    if ext == 'json':
        # Look for top-level keys
        import re
        keys = re.findall(r'"([^"]+)"\s*:', content)
        if keys:
            result += "## Structure (top-level keys):\n"
            for key in sorted(set(keys))[:20]:
                result += f"- \"{key}\"\n"
            if len(keys) > 20:
                result += f"... and {len(set(keys)) - 20} more keys\n"
    
    return result

def _truncate_dictionary_file(content: str, max_chars: int) -> str:
    """Handle dictionary/vocabulary files (common in ML models)"""
    lines = content.split('\n')
    
    # Calculate number of entries
    num_entries = len(lines)
    entry_sample_size = min(10, num_entries)
    
    # Take samples from beginning, middle and end
    beginning = '\n'.join(lines[:entry_sample_size])
    middle_start = max(0, num_entries // 2 - entry_sample_size // 2)
    middle = '\n'.join(lines[middle_start:middle_start+entry_sample_size])
    end_start = max(0, num_entries - entry_sample_size)
    ending = '\n'.join(lines[end_start:])
    
    # Build informative summary
    result = f"Dictionary/vocabulary file with {num_entries} entries ({len(content)} characters).\n\n"
    result += f"First {entry_sample_size} entries:\n{beginning}\n\n"
    result += f"Middle {entry_sample_size} entries:\n{middle}\n\n"
    result += f"Last {entry_sample_size} entries:\n{ending}\n\n"
    result += "[File truncated to show only sample entries]"
    
    return result

def _truncate_generic(content: str, max_chars: int) -> str:
    """Generic truncation for unknown file types"""
    half_size = max_chars // 2
    return content[:half_size] + f"\n\n...\n[Content truncated - file is {len(content)} characters]...\n\n" + content[-half_size:]

async def chat_with_repo(
    query: str, 
    code_context: str = "", 
    file_path: str = "",
    repo_owner: Optional[str] = None,
    repo_name: Optional[str] = None,
    repo_context: str = ""
) -> str:
    """Chat about repository code with context of the entire repository"""
    try:
        # Truncate large text files to prevent API token limit errors
        if code_context and file_path:
            code_context = truncate_large_text(code_context, file_path)
            
        # Also truncate repository context if it's too large
        if repo_context and len(repo_context) > 20000:
            repo_context = repo_context[:20000] + "\n\n...\n[Repository context truncated due to size]"
        
        # Check if the query is a greeting or general question
        is_greeting = is_greeting_or_general(query)
        
        # Prepare system message based on query type
        if is_greeting:
            system_message = """You are GitSage, a helpful assistant for GitHub repositories. 
You help users understand code repositories, explain code, and answer questions about software projects.
When greeting users, be friendly and brief, and mention that you can help them explore and understand the repository.
Always include info about the repository in your greeting if it's available.
"""
        else:
            system_message = """You are GitSage, a helpful AI assistant for understanding code repositories.
Focus on explaining code clearly and precisely with awareness of the entire repository structure.
Aim to provide useful technical insights about the code and repository organization.
Only make statements about the repository based on the information provided in the context.
"""

        # Create a prompt with all available context
        if is_greeting:
            # For greetings, provide a friendly response that includes repo info if available
            if repo_context:
                prompt = f"""User greeting: {query}
                
Repository context:
{repo_context}

Respond with a friendly greeting that mentions what the repository appears to be about.
Be brief but informative in your introduction."""
            else:
                prompt = f"""User greeting: {query}
                
Respond with a friendly greeting and offer to help understand the repository once a file is selected."""

        elif not code_context and not file_path:
            # General repository question
            prompt = f"""Repository context:
{repo_context}

Question: {query}

Please provide a clear and helpful response about this repository based on the available context."""
        else:
            # File-specific question
            prompt = f"""Repository context:
{repo_context}
Current file: {file_path}

Code:
{code_context}

Question: {query}

Please provide a clear and specific answer based on the code shown above and the repository context."""

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": system_message
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