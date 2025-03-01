from typing import Dict, List, Any, Optional, Tuple
from .github_service import read_file_content, get_directory_tree

def extract_repo_summary(owner: str, repo: str) -> Dict[str, Any]:
    """
    Extract a comprehensive summary of a repository including:
    - README content
    - Directory structure
    - Key file identification
    - Language statistics
    """
    # Get README summary
    readme_content = get_readme_content(owner, repo)
    
    # Get repo tree
    repo_tree = get_directory_tree(owner, repo)
    
    # Get language statistics and key files
    language_stats, key_files, top_level_dirs = analyze_repo_structure(repo_tree)
    
    # Put everything together
    summary = {
        "readme": readme_content,
        "tree": repo_tree,
        "languages": language_stats,
        "key_files": key_files,
        "top_level_dirs": top_level_dirs
    }
    
    return summary

def get_readme_content(owner: str, repo: str) -> str:
    """Get README content with fallbacks for different filenames"""
    # Try common README file names with different capitalizations
    readme_variants = [
        "README.md", "readme.md", "Readme.md", 
        "README.txt", "readme.txt",
        "README", "readme"
    ]
    
    for variant in readme_variants:
        content = read_file_content(owner, repo, variant)
        if content:
            return content
    
    return ""

def analyze_repo_structure(repo_tree: List) -> Tuple[Dict[str, int], List[str], List[str]]:
    """
    Analyze repository structure to identify:
    - Languages used (based on file extensions)
    - Key files (important configuration files)
    - Top-level directories (important for understanding project organization)
    """
    language_stats = {}
    key_files = []
    top_level_dirs = []
    
    def count_file_types(tree, path=""):
        nonlocal language_stats, key_files, top_level_dirs
        
        for item in tree:
            current_path = f"{path}/{item['name']}" if path else item['name']
            
            # Track top-level directories
            if not path and item['type'] == 'dir':
                top_level_dirs.append(item['name'])
            
            if item['type'] == 'file':
                # Extract file extension
                if '.' in item['name']:
                    ext = item['name'].split('.')[-1].lower()
                    language_stats[ext] = language_stats.get(ext, 0) + 1
                
                # Identify key files
                important_files = [
                    'requirements.txt', 'setup.py', 'package.json', 
                    'dockerfile', 'docker-compose.yml', '.env.example',
                    'main.py', 'app.py', 'index.py', 'run.py'
                ]
                
                if item['name'].lower() in important_files or current_path == 'app/__init__.py':
                    key_files.append(current_path)
            
            # Recursively process directories
            if 'children' in item:
                count_file_types(item['children'], current_path)
    
    count_file_types(repo_tree)
    return language_stats, key_files, top_level_dirs

def format_repo_context_for_prompt(repo_summary: Dict[str, Any]) -> str:
    """Format repository context information for an LLM prompt"""
    context = "Repository Overview:\n"
    
    # Add top-level directories first - these are most informative
    if repo_summary.get("top_level_dirs"):
        context += "\nTop-level Directories:\n"
        for directory in sorted(repo_summary["top_level_dirs"]):
            context += f"- {directory}/\n"
    
    # Add language statistics
    if repo_summary.get("languages"):
        context += "\nLanguages:\n"
        for lang, count in sorted(repo_summary["languages"].items(), key=lambda x: x[1], reverse=True):
            context += f"- {lang}: {count} files\n"
    
    # Add key files
    if repo_summary.get("key_files"):
        context += "\nKey Files:\n"
        for file in repo_summary["key_files"]:
            context += f"- {file}\n"
    
    # Format tree structure (simplified version)
    context += "\nRepository Structure:\n"
    
    def format_tree(nodes, indent=0, max_depth=3, current_depth=0):
        result = ""
        if current_depth > max_depth:
            return result
            
        for node in nodes:
            node_type = "📄" if node.get('type') == 'file' else "📁"
            result += f"{'  ' * indent}{node_type} {node.get('name', '')}\n"
            if node.get('children') and current_depth < max_depth:
                result += format_tree(node.get('children', []), indent + 1, max_depth, current_depth + 1)
        return result
    
    if repo_summary.get("tree"):
        context += format_tree(repo_summary["tree"])
    
    # Add README summary (first 2000 chars max)
    if repo_summary.get("readme"):
        context += "\nREADME Summary:\n"
        readme_summary = repo_summary["readme"][:2000]
        if len(repo_summary["readme"]) > 2000:
            readme_summary += "... (truncated)"
        context += readme_summary
    
    return context
