# 📧 Prompt-Driven Email Productivity Agent

**👨‍💻 Developed by:** Asneem Athar Shaik  
**🎓 Institution:** VIT-AP University  
**📧 GitHub:** [@asneem1234](https://github.com/asneem1234)

---

An intelligent AI-powered email management system that categorizes emails, extracts action items, generates draft replies, and provides a conversational RAG-powered chat interface for inbox management.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![Google Gemini](https://img.shields.io/badge/Gemini-2.5--Flash--Lite-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Features

- ✅ **Smart Email Categorization** - Color-coded tags (Urgent, Deadline, Conversation, Spam, Other)
- 🤖 **Prompt-Driven Architecture** - Fully customizable AI behavior through editable prompts
- 💬 **RAG-Powered Chat** - Conversational interface with semantic search across emails
- ✉️ **Draft Generation** - AI-generated professional replies (draft-only, never auto-sends)
- 📊 **Bulk Processing** - Categorize all emails at once with rate limit protection
- 🎨 **Gmail-Style UI** - Professional interface with Material Icons
- 🔒 **Safety First** - All AI actions create drafts for manual review

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

Before you begin, ensure you have:

- **Python 3.11+** installed ([Download here](https://www.python.org/downloads/))
- **Google Gemini API Key** (FREE - [Get it here](https://makersuite.google.com/app/apikey))
- **Git** installed ([Download here](https://git-scm.com/downloads))

---

## 📦 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/asneem1234/Prompt-Driven-Email-Productivity-Agent.git
cd Prompt-Driven-Email-Productivity-Agent
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `Flask==3.0.0` - Web framework
- `google-generativeai` - Gemini AI integration
- `python-dotenv` - Environment variable management
- `numpy==1.24.3` - Vector operations for RAG

---

## ⚙️ Configuration

### 1. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` and add your API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

> 💡 **Get your free API key:** Visit [Google AI Studio](https://makersuite.google.com/app/apikey)

### 2. Mock Inbox (Pre-loaded)

The application comes with **25 sample emails** in `data/mock_inbox.json`:
- Meeting requests
- Project updates  
- Urgent notifications
- Spam messages
- Task assignments

**No additional setup needed** - emails load automatically!

### 3. Configure Prompts (Optional)

Default prompts are in `data/default_prompts.json`. You can edit them:
- Through the UI: Navigate to **Custom Prompt** page
- Manually: Edit the JSON file directly

**Available prompts:**
1. **Categorization** - Email classification rules
2. **Action Extraction** - Task and deadline identification
3. **Auto-Reply** - Draft generation guidelines
4. **Summarization** - Email summary templates

---

## 🚀 Running the Application

### Start the Server

**Windows:**
```bash
python app.py
```

**Mac/Linux:**
```bash
python3 app.py
```

**Alternative (using run scripts):**
```bash
# Windows
run.bat

# Mac/Linux
./run.sh
```

### Access the Application

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

The application should automatically redirect to the **Inbox** page

---

## 📖 Usage Guide

### 1. **View Your Inbox**

Upon loading, you'll see:
- 25 pre-loaded emails
- Sender information
- Subject lines
- Timestamps
- Category badges (after categorization)

### 2. **Categorize Emails**

**Option A: Bulk Categorization**
1. Click the **"Categorize All"** button in the toolbar
2. Watch real-time progress as emails are processed
3. View color-coded badges:
   - 🔴 **RED** = Urgent
   - 🟠 **ORANGE** = Deadline
   - 🟢 **GREEN** = Conversation
   - ⚫ **GREY** = Spam
   - 🟤 **OTHER** = Uncategorized

**Option B: Individual Email**
- Click on any email to view details
- Categorization happens automatically

### 3. **Use the Email Agent Chat**

Navigate to **Chat** in the sidebar:

**Example Queries:**
```
"What are my urgent emails?"
"Tell me about emails from Chris Lee"
"What tasks do I need to complete?"
"Draft a reply to the meeting request"
"Show me all unread messages"
"Summarize my inbox"
```

The agent uses **RAG (Retrieval-Augmented Generation)** to:
- Search semantically across all emails
- Retrieve 3-5 most relevant messages
- Generate context-aware responses

### 4. **Customize Prompts**

Navigate to **Custom Prompt** (psychology icon):

1. Select a prompt type from dropdown
2. View the current prompt
3. Click **"Edit Prompt"**
4. Modify the text
5. Click **"Save Prompt"**
6. Optionally **"Test Prompt"** with sample data

**Prompt changes take effect immediately!**

### 5. **Manage Drafts**

Navigate to **Drafts**:
- View all AI-generated draft replies
- Click to read full content
- Edit or delete drafts
- Copy to your email client to send

**Safety Note:** Drafts are never sent automatically!

---

## 📁 Project Structure

```
Prompt-Driven-Email-Productivity-Agent/
│
├── app.py                      # Main Flask application
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── src/                        # Core application modules
│   ├── llm_client.py          # Gemini AI integration
│   ├── email_processor.py     # Email categorization
│   ├── email_agent.py         # RAG-powered chat agent
│   ├── rag_system.py          # Semantic search
│   ├── prompt_manager.py      # Prompt management
│   └── draft_manager.py       # Draft handling
│
├── templates/                  # HTML templates
│   ├── base.html              # Base layout
│   ├── inbox.html             # Email list
│   ├── chat.html              # Chat interface
│   ├── drafts.html            # Draft management
│   └── prompt_brain.html      # Prompt editor
│
├── static/
│   └── style.css              # Gmail-style CSS
│
├── data/
│   ├── mock_inbox.json        # 25 sample emails
│   └── default_prompts.json   # AI prompts
│
└── docs/                       # Documentation
    ├── ARCHITECTURE.md
    ├── ASSIGNMENT_COMPLIANCE.md
    ├── DEMO_VIDEO_SCRIPT.md
    ├── PROJECT_STRUCTURE.md
    └── QUICKSTART.md
```

---

## 📚 Documentation

Detailed documentation available in `docs/`:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - System design and component overview
- **[PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)** - Complete codebase organization
- **[QUICKSTART.md](docs/QUICKSTART.md)** - Fast setup guide
- **[DEMO_VIDEO_SCRIPT.md](docs/DEMO_VIDEO_SCRIPT.md)** - Complete demo walkthrough
- **[ASSIGNMENT_COMPLIANCE.md](docs/ASSIGNMENT_COMPLIANCE.md)** - Requirements checklist

---

## 🐛 Troubleshooting

### Application won't start

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
pip install -r requirements.txt
```

---

### API Key Issues

**Error:** `GEMINI_API_KEY not found`

**Solution:**
1. Check `.env` file exists in project root
2. Verify API key is correct
3. Ensure no spaces around the `=` sign
4. Restart the application

---

### Rate Limit Errors

**Error:** `429 Quota exceeded`

**Explanation:** Free tier has limits:
- 15 requests per minute
- 250 requests per day

**Solutions:**
1. Wait 60 seconds between bulk operations
2. Use the built-in delay (4 seconds between emails)
3. Upgrade to paid tier: [Google AI Pricing](https://ai.google.dev/pricing)

---

### Categorization Returns "Other"

**Possible Causes:**
1. API quota exhausted
2. Network connectivity issues
3. Prompt formatting errors

**Solutions:**
1. Check API key is valid
2. Verify internet connection
3. Reset prompts to default in Custom Prompt page

---

### Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Mac/Linux
lsof -ti:5000 | xargs kill -9
```

---

## 🎥 Demo Video

Watch a complete walkthrough: [Coming Soon]

**What's demonstrated:**
- Loading the inbox
- Editing custom prompts
- Bulk email categorization
- Using the chat agent
- Managing drafts

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Asneem Athar Shaik**  
VIT-AP University

- GitHub: [@asneem1234](https://github.com/asneem1234)
- Repository: [Prompt-Driven-Email-Productivity-Agent](https://github.com/asneem1234/Prompt-Driven-Email-Productivity-Agent)

---

## 🙏 Acknowledgments

- Google Gemini AI for the LLM capabilities
- Flask framework for the web backend
- Material Icons for UI elements
- Gmail for design inspiration

---

## 📞 Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [Documentation](docs/)
3. Open an issue on GitHub

---

**Built with ❤️ using Flask, Python, and Google Gemini AI**

### Using Docker (Optional)

```bash
# Build the image
docker build -t email-agent .

# Run the container
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key email-agent
```

### Deploy to Cloud

The app can be deployed to:
- **Streamlit Cloud**: Push to GitHub and connect
- **Heroku**: Use the included Dockerfile
- **AWS/Azure/GCP**: Deploy as a container or Python app

## 🤝 Contributing

This is a hiring challenge submission. For evaluation purposes only.

## 📄 License

This project is submitted as part of a hiring challenge.

## 👤 Author

**GitHub**: [@asneem1234](https://github.com/asneem1234)

## 📞 Support

For questions or issues, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit, Google Gemini AI (FREE), and Python**
