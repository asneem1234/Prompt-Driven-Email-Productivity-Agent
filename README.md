# 📧 Email Productivity Agent

A prompt-driven intelligent email productivity system that automatically categorizes emails, extracts action items, generates draft replies, and provides a conversational chat interface for inbox management.

## 🎯 Key Features

- **📥 Smart Inbox Management**: Load and process emails with automatic categorization
- **🏷️ AI-Powered Categorization**: Intelligently sorts emails into Important, Newsletter, Spam, To-Do, and Meeting
- **✅ Action Item Extraction**: Automatically identifies tasks, deadlines, and priorities
- **✉️ Draft Generation**: Creates professional email replies (never sends automatically)
- **🧠 Prompt Brain**: Fully customizable prompt templates that control agent behavior
- **💬 Email Agent Chat**: Natural language interface for querying and managing your inbox
- **🔒 Safety First**: All drafts are saved locally and never sent automatically
- **📊 Real-time Analytics**: Track email categories and action items

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key (FREE - get it from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/asneem1234/Prompt-Driven-Email-Productivity-Agent.git
   cd Prompt-Driven-Email-Productivity-Agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (Optional - can also enter in UI)
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   - The app will automatically open at `http://localhost:8501`
   - If not, navigate to that URL manually

## 📖 Usage Guide

### 1. Initial Setup

1. Get your FREE Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Enter your Gemini API key in the sidebar
3. Click "Initialize Application"
4. Wait for the success message

### 2. Load Mock Inbox

1. Click "📂 Load Inbox" in the sidebar
2. The system will load 15 sample emails
3. Click "⚡ Process All" to analyze all emails

### 3. Browse Your Inbox

- View categorized emails in the main inbox view
- Filter by category (Important, Newsletter, Spam, To-Do, Meeting)
- Click "👁️ View" on any email to see details
- Expand emails to see summaries and action items

### 4. Configure Prompts (Prompt Brain)

1. Navigate to "🧠 Prompt Brain"
2. Select a prompt type to edit:
   - **Categorization**: Controls how emails are sorted
   - **Action Extraction**: Defines how tasks are identified
   - **Auto-Reply**: Shapes draft reply generation
   - **Summarization**: Controls email summaries
3. Edit the prompt template (use `{sender}`, `{subject}`, `{body}` placeholders)
4. Test your prompt on sample emails
5. Save changes

### 5. Generate Draft Replies

1. Select an email in the inbox
2. Click "✍️ Draft Reply"
3. Review the generated draft in the "✉️ Drafts" page
4. Export or delete drafts as needed

### 6. Chat with Your Inbox

1. Go to "💬 Email Agent Chat"
2. Ask questions like:
   - "What tasks do I need to do?"
   - "Show me all urgent emails"
   - "Summarize the email from Alice"
   - "Which emails need my response?"
3. Use quick action buttons for common queries

## 🗂️ Project Structure

```
Prompt-Driven-Email-Productivity-Agent/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
├── .gitignore                      # Git ignore file
├── README.md                       # This file
├── data/
│   ├── mock_inbox.json            # Sample emails (15 emails)
│   ├── default_prompts.json       # Default prompt templates
│   └── drafts.json                # Saved drafts (generated)
└── src/
    ├── __init__.py
    ├── llm_client.py              # LLM integration with call logging
    ├── prompt_manager.py          # Prompt template management
    ├── email_processor.py         # Email processing pipeline
    ├── draft_manager.py           # Draft generation and storage
    └── email_agent.py             # Conversational agent
```

## 🧠 Prompt Templates

The system uses four main prompt types:

### 1. Categorization Prompt
Categorizes emails into: Important, Newsletter, Spam, To-Do, Meeting

### 2. Action Extraction Prompt
Extracts tasks with deadlines and priorities in JSON format

### 3. Auto-Reply Prompt
Generates professional draft replies based on email context

### 4. Summarization Prompt
Creates concise summaries with key points and urgency levels

**All prompts are fully customizable through the Prompt Brain interface!**

## 🔧 Configuration

### Using Different LLM Models

The system uses Google Gemini by default (FREE). To use a different Gemini model, edit `src/llm_client.py`, line 19:

```python
def __init__(self, model: str = "gemini-1.5-pro"):  # Change model here
    # Options: gemini-1.5-flash (fast), gemini-1.5-pro (smarter)
```

### Customizing Email Categories

Edit the categorization prompt in the Prompt Brain to add/modify categories.

## 📋 Mock Inbox Details

The `data/mock_inbox.json` contains 15 diverse sample emails:

- Meeting requests (with scheduling needs)
- Task assignments (with deadlines)
- Newsletters (marketing content)
- Spam/scam emails
- Status updates
- Follow-up requests
- Security alerts
- Contract reviews
- Payment reminders

## 🎥 Demo Video

**Demo Video Link**: [Add your video link here after recording]

### Demo Video Timestamps:
- 0:00 - Introduction and project overview
- 0:30 - Loading mock inbox
- 1:30 - Email categorization and processing
- 2:30 - Prompt Brain: Editing and testing prompts
- 3:30 - Draft generation
- 4:30 - Email Agent chat interface
- 5:30 - Advanced features and wrap-up

## 🛡️ Safety Features

- **No Automatic Sending**: All generated emails are saved as drafts only
- **API Key Security**: Keys are never stored in code or committed to git
- **Error Handling**: Graceful degradation when LLM calls fail
- **Data Privacy**: All processing happens locally; emails never leave your system except for LLM API calls

## 🧪 Testing

Run basic tests:

```bash
python -c "from src.llm_client import LLMClient; print('✅ Imports successful')"
```

## 🚢 Deployment

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
