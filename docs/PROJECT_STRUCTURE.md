# Project Structure

```
Prompt-Driven-Email-Productivity-Agent/
│
├── app.py                          # Main Flask application entry point
│
├── src/                            # Core application modules
│   ├── __init__.py                # Package initializer
│   ├── llm_client.py              # LLM integration with Gemini 2.0 Flash
│   ├── email_processor.py         # Email categorization & processing
│   ├── email_agent.py             # RAG-powered conversational agent
│   ├── rag_system.py              # Retrieval-Augmented Generation system
│   ├── prompt_manager.py          # Prompt storage and management
│   └── draft_manager.py           # Draft email management
│
├── templates/                      # HTML templates (Jinja2)
│   ├── base.html                  # Base template with sidebar
│   ├── inbox.html                 # Email inbox view
│   ├── chat.html                  # Chat interface
│   ├── drafts.html                # Drafts management
│   ├── prompt_brain.html          # Prompt editor
│   └── compose.html               # Email composition
│
├── static/                         # Static assets
│   └── style.css                  # Gmail-style CSS
│
├── data/                          # Data files
│   ├── mock_inbox.json           # 25 sample emails
│   └── default_prompts.json      # Default AI prompts
│
├── .github/                       # GitHub configuration
│   └── workflows/                # CI/CD workflows
│
├── requirements.txt               # Python dependencies
├── vercel.json                    # Vercel deployment config
├── Dockerfile                     # Docker containerization
├── .env.example                   # Environment variables template
├── .gitignore                     # Git ignore rules
│
├── README.md                      # Main documentation
├── ARCHITECTURE.md                # System architecture details
├── ASSIGNMENT_COMPLIANCE.md       # Assignment requirements checklist
├── DEMO_VIDEO_SCRIPT.md          # Video demonstration script
├── QUICKSTART.md                  # Quick setup guide
│
└── run.bat / run.sh              # Platform-specific run scripts
```

## Core Modules

### `app.py`
- Flask application initialization
- Route definitions for all pages
- Session management
- API endpoints for chat, categorization, drafts

### `src/llm_client.py`
- Gemini 2.0 Flash integration
- Retry logic for rate limits
- Error handling for API calls
- Prompt formatting and response parsing

### `src/email_processor.py`
- Email categorization (Urgent/Deadline/Conversation/Spam/Other)
- Action item extraction
- Email summarization
- Batch processing with rate limit protection

### `src/email_agent.py`
- RAG-powered chat interface
- Natural language query processing
- Email retrieval and context building
- Draft generation from queries

### `src/rag_system.py`
- Keyword-based embeddings
- Cosine similarity search
- Email indexing (25 emails)
- Context retrieval (3-5 emails)

### `src/prompt_manager.py`
- Load/save prompts from JSON
- Prompt template formatting
- User customization support
- Test prompt functionality

### `src/draft_manager.py`
- Draft creation and storage
- Draft editing capabilities
- Draft retrieval
- No auto-send safety

## Data Files

### `data/mock_inbox.json`
- 25 diverse sample emails
- Real-world scenarios (meetings, tasks, spam)
- Complete with sender, subject, body, timestamps

### `data/default_prompts.json`
- Categorization prompt (color-coded)
- Action extraction prompt
- Auto-reply draft prompt
- Summarization prompt

## Templates Structure

All templates extend `base.html` which provides:
- Gmail-style sidebar navigation
- Material Icons integration
- Responsive header
- Consistent styling

## Code Organization Principles

1. **Separation of Concerns**: Each module has a single responsibility
2. **Modular Design**: Components can be used independently
3. **Clear Naming**: Files and functions have descriptive names
4. **Documentation**: Each module has docstrings
5. **Error Handling**: Comprehensive try-catch blocks
6. **Configuration**: Environment variables for sensitive data
7. **Type Hints**: Python type annotations where applicable
8. **Session Management**: User state isolated per session

## Dependencies

Core packages (from `requirements.txt`):
- `Flask==3.0.0` - Web framework
- `google-generativeai` - Gemini AI integration
- `python-dotenv` - Environment configuration
- `numpy==1.24.3` - Vector operations for RAG

## Deployment

- **Development**: `python app.py` (localhost:5000)
- **Production**: Vercel serverless (vercel.json config)
- **Docker**: Dockerfile for containerization
