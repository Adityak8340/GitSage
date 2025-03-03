<div align="center">
  <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" width="150" height="150"/>
  <h1 style="color: #58a6ff;">🔍 GitSage</h1>
  <p><i>Your AI-powered GitHub repository explorer!</i></p>

  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
  [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/adityak8340/GitSage)
  [![Groq](https://img.shields.io/badge/🤖%20Groq-API-yellow)](https://groq.com)
</div>

<div align="center">
  <img src="app/static/img/preview.png" alt="GitSage Preview" style="width: 100%; max-width: 800px; border-radius: 10px; margin: 20px 0; box-shadow: 0 4px 8px rgba(0,0,0,0.1);"/>
</div>

---

<div align="center" style="margin: 30px 0;">
  <h3 style="color: #58a6ff;">✨ Features</h3>
</div>

- 🔍 **Interactive Explorer**: Navigate repository files with ease
- 🤖 **AI Analysis**: Get instant code explanations and insights
- 💬 **Smart Chat**: Ask questions about any code file
- 🎨 **Modern UI**: Dark mode interface with smooth animations
- 📊 **Code Metrics**: Analyze complexity and patterns
- ⚡ **Real-time**: Instant file viewing and parsing

---

<div align="center" style="margin: 30px 0;">
  <h3 style="color: #58a6ff;">🚀 Quick Start</h3>
</div>

1. **Clone the repository**
```bash
git clone https://github.com/adityak8340/GitSage.git
cd GitSage
```

2. **Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```properties
GITHUB_TOKEN="your-github-token"
GROQ_API_KEY="your-groq-api-key"
```

5. **Run the application**
```bash
python run.py
```

Visit `http://localhost:8000` in your browser 🌐

---

<div align="center" style="margin: 30px 0;">
  <h3 style="color: #58a6ff;">🛠️ Architecture</h3>
</div>

```mermaid
graph LR
    A[GitHub Repo] --> B[GitSage Backend]
    B --> C[File Parser]
    B --> D[AI Analysis]
    C --> E[Web Interface]
    D --> E
    E --> F[User Insights]
```

---

<div align="center" style="margin: 30px 0;">
  <h3 style="color: #58a6ff;">💡 Usage Example</h3>
</div>

<div style="width: 100%; background-color: #1a1a1a; padding: 15px; border-radius: 6px;">

```python
# Just paste a GitHub repository URL
"https://github.com/username/repo"

# GitSage provides instant insights
"💡 Analysis shows this is a Python web application 
 with FastAPI backend. Main features include..."
```

</div>

---

<div align="center" style="margin: 30px 0;">
  <h3 style="color: #58a6ff;">🔮 Coming Soon</h3>
</div>

- [ ] Repository comparison tools
- [ ] Code quality scoring
- [ ] Multiple AI model support
- [ ] Team collaboration features
- [ ] Custom analysis plugins
- [ ] Repository issue tracking and PR automation

---

<div align="center">
  <div class="tech-stack" style="display: flex; justify-content: center; gap: 20px; margin: 20px 0;">
    <img src="https://www.vectorlogo.zone/logos/python/python-icon.svg" width="50" height="50"/>
    <img src="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png" width="50" height="50"/>
    <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/github/github-original.svg" width="50" height="50"/>
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/javascript/javascript-original.svg" width="50" height="50"/>
  </div>
</div>

<div align="center">
    <br>
    <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&pause=1000&color=58A6FF&center=true&vCenter=true&width=435&lines=Built+with+%E2%9D%A4%EF%B8%8F;Feel+free+to+contribute!" alt="Typing SVG" />
    <p align="center">
        <img src="https://img.shields.io/github/stars/Adityak8340/GitSage?style=social" alt="Stars">
        <img src="https://img.shields.io/github/forks/Adityak8340/GitSage?style=social" alt="Forks">
        <img src="https://img.shields.io/github/issues/Adityak8340/GitSage?style=social" alt="Issues">
    </p>
</div>
