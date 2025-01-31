from flask import Blueprint, jsonify, request, render_template
from ..services.github_service import (
    get_repo_info, get_repo_contents, read_file_content,
    get_directory_tree, analyze_complexity,
    get_dependencies, get_commit_history
)
from ..services.ai_service import get_code_explanation, chat_with_repo

bp = Blueprint('repo', __name__, url_prefix='/repo')

@bp.route('/')
def index():
    """Repository index page"""
    return render_template('index.html')

@bp.route('/<owner>/<repo>')
def get_repository(owner, repo):
    """Get repository information"""
    repo_info = get_repo_info(owner, repo)
    if isinstance(repo_info, tuple):
        return jsonify(repo_info[0]), repo_info[1]
    return render_template('repository.html', repo=repo_info)

@bp.route('/<owner>/<repo>/contents/<path:file_path>')
def get_file_content(owner, repo, file_path):
    """Get content of a specific file"""
    content = read_file_content(owner, repo, file_path)
    if content is None:
        return jsonify({"error": "File not found or unable to read"}), 404
    return jsonify({"content": content})

@bp.route('/<owner>/<repo>/contents/')
@bp.route('/<owner>/<repo>/contents/<path:path>')
def list_contents(owner, repo, path=""):
    """List repository contents at a specific path"""
    contents = get_repo_contents(owner, repo, path)
    return jsonify(contents)

@bp.route('/<owner>/<repo>/tree')
def get_tree(owner, repo):
    """Get repository directory tree"""
    tree = get_directory_tree(owner, repo)
    return jsonify(tree)

@bp.route('/<owner>/<repo>/analyze')
def analyze_repository(owner, repo):
    """Analyze repository complexity and dependencies"""
    complexity = analyze_complexity(owner, repo)
    dependencies = get_dependencies(owner, repo)
    return jsonify({
        "complexity": complexity,
        "dependencies": dependencies
    })

@bp.route('/<owner>/<repo>/history')
def get_history(owner, repo):
    """Get repository commit history"""
    history = get_commit_history(owner, repo)
    return jsonify(history)

@bp.route('/explain', methods=['POST'])
def explain_code_route():
    """Explain code using AI"""
    data = request.json
    explanation = get_code_explanation(data['code'], data['path'])
    return jsonify({"text": explanation})

@bp.route('/chat', methods=['POST'])
def chat():
    """Chat about repository code"""
    data = request.json
    query = data.get('query', '')
    context = data.get('context', {})
    
    try:
        # Get file content and path from context
        file_content = context.get('content', '')
        file_path = context.get('path', '')
        
        # Get response from AI service with context
        response = chat_with_repo(
            query=query,
            code_context=file_content,
            file_path=file_path
        )
        return jsonify({"text": response})
    except Exception as e:
        return jsonify({"error": f"Chat error: {str(e)}"}), 500
