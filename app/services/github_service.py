import requests
import base64
from flask import current_app
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
import re
from collections import defaultdict

def get_repo_info(owner, repo):
    """
    Fetch repository information from GitHub API using token
    """
    token = current_app.config.get('GITHUB_TOKEN')
    url = f"https://api.github.com/repos/{owner}/{repo}"
    headers = {"Authorization": f"token {token}"}
    
    # Configure retry strategy
    session = requests.Session()
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    
    try:
        response = session.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Failed to fetch repository: {response.status_code}"}, response.status_code
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error occurred: {str(e)}"}, 500

def get_repo_contents(owner, repo, path=""):
    """
    Fetch contents of a repository path
    """
    token = current_app.config.get('GITHUB_TOKEN')
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.RequestException:
        return []

def read_file_content(owner, repo, file_path):
    """
    Read content of a specific file from repository
    """
    token = current_app.config.get('GITHUB_TOKEN')
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
    headers = {"Authorization": f"token {token}"}

    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            file_data = response.json()
            if file_data.get("encoding") == "base64":
                content = base64.b64decode(file_data["content"]).decode("utf-8")
                return content
        return None
    except (requests.exceptions.RequestException, UnicodeDecodeError):
        return None

def get_directory_tree(owner, repo):
    """Get complete directory structure of the repository"""
    token = current_app.config.get('GITHUB_TOKEN')
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/main?recursive=1"
    headers = {"Authorization": f"token {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            tree_data = response.json()
            tree = []
            for item in tree_data.get('tree', []):
                path_parts = item['path'].split('/')
                current_level = tree
                for i, part in enumerate(path_parts):
                    # Find or create node at current level
                    node = next((n for n in current_level if n['name'] == part), None)
                    if node is None:
                        node = {
                            'name': part,
                            'path': '/'.join(path_parts[:i+1]),
                            'type': 'file' if i == len(path_parts)-1 and item['type'] == 'blob' else 'dir',
                            'children': []
                        }
                        current_level.append(node)
                    current_level = node['children']
            return tree
        return []
    except requests.exceptions.RequestException:
        return []

def analyze_complexity(owner, repo):
    """Analyze code complexity of the repository"""
    files = get_all_python_files(owner, repo)
    complexity_data = {}
    
    for file_path in files:
        content = read_file_content(owner, repo, file_path)
        if content:
            complexity_data[file_path] = {
                'cyclomatic_complexity': calculate_cyclomatic_complexity(content),
                'lines_of_code': len(content.splitlines()),
                'functions': analyze_functions(content)
            }
    
    return complexity_data

def get_dependencies(owner, repo):
    """Extract dependencies from repository"""
    dependencies = {
        'python': get_python_dependencies(owner, repo),
        'javascript': get_js_dependencies(owner, repo)
    }
    return dependencies

def get_commit_history(owner, repo):
    """Get repository commit history"""
    token = current_app.config.get('GITHUB_TOKEN')
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    headers = {"Authorization": f"token {token}"}
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            commits = response.json()
            return [{
                'sha': commit['sha'],
                'author': commit['commit']['author']['name'],
                'date': commit['commit']['author']['date'],
                'message': commit['commit']['message']
            } for commit in commits]
        return []
    except requests.exceptions.RequestException:
        return []

def get_all_python_files(owner, repo):
    """Get all Python files in the repository"""
    tree = get_directory_tree(owner, repo)
    python_files = []
    
    def traverse(node, files):
        if node['type'] == 'file' and node['name'].endswith('.py'):
            files.append(node['path'])
        for child in node.get('children', []):
            traverse(child, files)
    
    for node in tree:
        traverse(node, python_files)
    return python_files

def calculate_cyclomatic_complexity(code):
    """Calculate cyclomatic complexity of Python code"""
    # Simple implementation - counts control flow statements
    control_structures = len(re.findall(r'\b(if|for|while|except|with|def|class)\b', code))
    return control_structures + 1

def analyze_functions(code):
    """Analyze functions in Python code"""
    functions = []
    for match in re.finditer(r'def\s+(\w+)\s*\((.*?)\):', code):
        functions.append({
            'name': match.group(1),
            'parameters': [p.strip() for p in match.group(2).split(',') if p.strip()],
            'line_number': len(code[:match.start()].splitlines()) + 1
        })
    return functions

def get_python_dependencies(owner, repo):
    """Extract Python dependencies from requirements.txt"""
    content = read_file_content(owner, repo, 'requirements.txt')
    if content:
        return [line.strip() for line in content.splitlines() if line.strip()]
    return []

def get_js_dependencies(owner, repo):
    """Extract JavaScript dependencies from package.json"""
    content = read_file_content(owner, repo, 'package.json')
    if content:
        try:
            import json
            data = json.loads(content)
            return {
                'dependencies': data.get('dependencies', {}),
                'devDependencies': data.get('devDependencies', {})
            }
        except json.JSONDecodeError:
            return {}
    return {}
