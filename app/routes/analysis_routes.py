from flask import Blueprint, render_template, jsonify, request
import requests
import base64
from app.config import Config

repo_bp = Blueprint('repo', __name__)

@repo_bp.route('/')
def index():
    return render_template('index.html')

@repo_bp.route('/repo/<owner>/<repo>')
def repo_overview(owner, repo):
    # Implement repository overview logic
    headers = {'Authorization': f'token {Config.GITHUB_TOKEN}'}
    repo_url = f'https://api.github.com/repos/{owner}/{repo}'
    
    repo_info = requests.get(repo_url, headers=headers).json()
    return render_template('dashboard.html', repo=repo_info)

@repo_bp.route('/api/files/<owner>/<repo>')
def get_files(owner, repo):
    # Implement file listing logic
    return jsonify({'files': []})