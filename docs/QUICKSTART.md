# 🚀 Quick Start Guide

Get the Email Productivity Agent running in 3 minutes!

## Step-by-Step Setup

### 1️⃣ Prerequisites
- Python 3.8 or higher ([Download](https://www.python.org/downloads/))
- OpenAI API Key ([Get one here](https://platform.openai.com/api-keys))
- Git (optional, for cloning)

### 2️⃣ Installation

**Option A: Quick Start (Recommended)**
```bash
# Clone or download the repository
git clone https://github.com/asneem1234/Prompt-Driven-Email-Productivity-Agent.git
cd Prompt-Driven-Email-Productivity-Agent

# Windows
run.bat

# Linux/Mac
chmod +x run.sh
./run.sh
```

**Option B: Manual Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

**Option C: Docker**
```bash
# Build and run with Docker
docker build -t email-agent .
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key email-agent
```

### 3️⃣ First Run

1. **Open your browser** at `http://localhost:8501`
2. **Enter your OpenAI API Key** in the sidebar
3. **Click "Initialize Application"**
4. **Click "📂 Load Inbox"** to load sample emails
5. **Click "⚡ Process All"** to analyze emails

🎉 **You're ready!** Start exploring the inbox, editing prompts, and chatting with your emails.

## 📱 Basic Usage

### View Emails
- Browse categorized emails in the **📥 Inbox** tab
- Click "👁️ View" to see email details
- Expand summaries to see action items

### Edit Prompts
- Go to **🧠 Prompt Brain** tab
- Select a prompt to edit
- Test it on sample emails
- Save your changes

### Generate Drafts
- Select an email in the inbox
- Click "✍️ Draft Reply"
- View drafts in the **✉️ Drafts** tab
- Export or delete as needed

### Chat with Inbox
- Go to **💬 Email Agent Chat** tab
- Ask questions like:
  - "What tasks do I need to do?"
  - "Show me urgent emails"
  - "Summarize the email from Alice"

## 🔧 Configuration

### Using a Different LLM Model
Edit `src/llm_client.py`, line 17:
```python
def __init__(self, model: str = "gpt-4"):  # Change model here
```

### Adding Your Own Emails
Edit `data/mock_inbox.json` with your email structure:
```json
{
  "id": "custom_001",
  "sender": "someone@example.com",
  "sender_name": "Someone",
  "subject": "Your subject",
  "timestamp": "2025-11-23T10:00:00Z",
  "body": "Email body here...",
  "thread_id": "thread_001"
}
```

### Custom Categories
Edit the categorization prompt in the Prompt Brain to add/modify categories.

## ❓ Troubleshooting

**Issue: "OPENAI_API_KEY not found"**
- Solution: Enter your API key in the sidebar or add it to `.env` file

**Issue: "Module not found"**
- Solution: Run `pip install -r requirements.txt`

**Issue: "Port 8501 already in use"**
- Solution: Run `streamlit run app.py --server.port 8502`

**Issue: "LLM call failed"**
- Solution: Check your API key and internet connection

## 📚 Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Check out [DEMO_SCRIPT.md](DEMO_SCRIPT.md) for video recording guide
- Explore the code in `src/` directory
- Customize prompts in the Prompt Brain

## 💡 Tips

- Use **Ctrl+C** in terminal to stop the server
- Press **R** in the Streamlit app to refresh
- All data is saved locally in `data/` folder
- Drafts are never sent automatically (safety first!)

## 🎬 Watch the Demo

[Link to demo video will be added here]

## 📞 Need Help?

- Check existing issues on GitHub
- Open a new issue with details
- Review the [CONTRIBUTING.md](CONTRIBUTING.md) guide

---

**Happy emailing! 📧✨**
