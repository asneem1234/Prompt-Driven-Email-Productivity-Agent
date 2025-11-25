# Architecture Documentation

## System Overview

The Email Productivity Agent is a prompt-driven system that processes emails through a customizable LLM pipeline.

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI (app.py)                │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌──────────────┐ │
│  │  Inbox  │ │ Prompt  │ │ Drafts  │ │ Agent Chat   │ │
│  │  View   │ │  Brain  │ │  View   │ │              │ │
│  └─────────┘ └─────────┘ └─────────┘ └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Backend Services                      │
│                                                          │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │ EmailProcessor   │──────│  PromptManager   │        │
│  │                  │      │                  │        │
│  │ - Categorize     │      │ - Load prompts   │        │
│  │ - Extract actions│      │ - Format prompts │        │
│  │ - Summarize      │      │ - Save versions  │        │
│  └──────────────────┘      └──────────────────┘        │
│           │                          │                  │
│           ▼                          ▼                  │
│  ┌──────────────────┐      ┌──────────────────┐        │
│  │  DraftManager    │      │   EmailAgent     │        │
│  │                  │      │                  │        │
│  │ - Generate drafts│      │ - Chat queries   │        │
│  │ - Save locally   │      │ - Context aware  │        │
│  └──────────────────┘      └──────────────────┘        │
│           │                          │                  │
│           └──────────┬───────────────┘                  │
│                      ▼                                  │
│            ┌──────────────────┐                         │
│            │   LLM Client     │                         │
│            │                  │                         │
│            │ - Call OpenAI    │                         │
│            │ - Log calls      │                         │
│            │ - Error handling │                         │
│            └──────────────────┘                         │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   Data Storage (JSON)                    │
│                                                          │
│  • mock_inbox.json      - Sample emails                 │
│  • default_prompts.json - Prompt templates              │
│  • drafts.json          - Generated drafts (runtime)    │
└─────────────────────────────────────────────────────────┘
```

## Component Details

### 1. LLM Client (`src/llm_client.py`)

**Responsibility:** Single point of interaction with LLM API

**Key Features:**
- Configurable model selection
- JSON mode support
- Call history logging
- Error handling and retry logic

**API:**
```python
client = LLMClient(model="gpt-3.5-turbo")
result = client.call_llm(
    prompt="Your prompt here",
    temperature=0.7,
    json_mode=True
)
```

### 2. Prompt Manager (`src/prompt_manager.py`)

**Responsibility:** Manage prompt templates and versioning

**Key Features:**
- Load/save prompts from JSON
- Template formatting with placeholders
- Version history tracking
- CRUD operations on prompts

**API:**
```python
pm = PromptManager()
prompts = pm.get_all_prompts()
formatted = pm.format_prompt("categorization", email_data)
pm.update_prompt("categorization", new_prompt_data)
```

### 3. Email Processor (`src/email_processor.py`)

**Responsibility:** Process emails through LLM pipeline

**Key Features:**
- Batch processing
- Categorization
- Action item extraction
- Summarization
- Error collection

**Pipeline:**
```
Email → Categorize → Extract Actions → Summarize → Store
```

**API:**
```python
processor = EmailProcessor(llm_client, prompt_manager)
results = processor.process_inbox(emails)
actions = processor.get_all_action_items()
```

### 4. Draft Manager (`src/draft_manager.py`)

**Responsibility:** Generate and manage email drafts

**Key Features:**
- Reply draft generation
- New email composition
- Local storage (no sending)
- Export functionality

**API:**
```python
draft_mgr = DraftManager(llm_client, prompt_manager)
result = draft_mgr.generate_reply_draft(email)
draft = draft_mgr.get_draft(draft_id)
text = draft_mgr.export_draft_as_text(draft_id)
```

### 5. Email Agent (`src/email_agent.py`)

**Responsibility:** Conversational interface for inbox queries

**Key Features:**
- Context-aware responses
- Query processing
- Conversation history
- Quick actions

**API:**
```python
agent = EmailAgent(llm_client, email_processor)
result = agent.query(
    "What tasks do I need to do?",
    selected_email=email,
    context_emails=inbox
)
```

## Data Flow

### Email Processing Flow
```
1. User clicks "Process All"
   ↓
2. Load emails from mock_inbox.json
   ↓
3. For each email:
   a. Format categorization prompt
   b. Call LLM → Get category
   c. Format action extraction prompt
   d. Call LLM → Get action items
   e. Format summarization prompt
   f. Call LLM → Get summary
   ↓
4. Store processed results in memory
   ↓
5. Update UI with categories and stats
```

### Draft Generation Flow
```
1. User selects email and clicks "Draft Reply"
   ↓
2. Format auto-reply prompt with email data
   ↓
3. Call LLM with prompt
   ↓
4. Parse JSON response
   ↓
5. Create draft object with metadata
   ↓
6. Save to drafts.json
   ↓
7. Display in Drafts tab
```

### Chat Query Flow
```
1. User types question in chat
   ↓
2. Build context from:
   - Selected email (if any)
   - Inbox statistics
   - Processed email data
   ↓
3. Construct agent prompt with context
   ↓
4. Call LLM
   ↓
5. Parse response with answer and actions
   ↓
6. Display in chat interface
```

## Prompt Engineering

### Prompt Structure
All prompts follow this pattern:
```
1. Role definition ("You are a [role]")
2. Task description
3. Guidelines/rules
4. Input data (email details)
5. Output format specification (JSON schema)
```

### Example: Categorization Prompt
```
You are an email categorization assistant.

Categorize into: Important, Newsletter, Spam, To-Do, Meeting

Guidelines:
- Important: Critical business...
- Newsletter: Marketing...
[etc]

Email Details:
From: {sender}
Subject: {subject}
Body: {body}

Respond in JSON: {"category": "...", "confidence": 0.9}
```

## Security Considerations

### API Key Management
- Never committed to git
- Stored in environment or entered in UI
- Not logged or exposed

### Draft Safety
- All drafts saved locally
- No automatic sending
- Explicit "draft" status

### Error Handling
- LLM failures don't crash app
- Graceful degradation
- User-friendly error messages

## Performance

### Optimization Strategies
1. **Batch Processing**: Process multiple emails in sequence
2. **Caching**: Store processed results in memory
3. **Lazy Loading**: Load data only when needed
4. **Temperature Tuning**: Lower temp (0.3) for categorization, higher (0.7) for drafts

### Scalability
Current limits:
- In-memory storage (suitable for demo)
- Sequential LLM calls (no parallelization)
- Single user (no authentication)

For production:
- Use database (PostgreSQL)
- Implement async LLM calls
- Add caching layer (Redis)
- Add authentication

## Extension Points

### Adding New Prompt Types
1. Add to `default_prompts.json`
2. Create processing method in `EmailProcessor`
3. Add UI in Streamlit app

### Supporting New LLM Providers
1. Edit `LLMClient.__init__`
2. Adjust API call format
3. Update error handling

### Adding Real Email Integration
1. Add email provider SDK (Gmail, Outlook)
2. Implement OAuth flow
3. Add sync logic
4. Update UI for account connection

## Testing Strategy

### Unit Tests
- Test each module in isolation
- Mock LLM responses
- Verify data transformations

### Integration Tests
- Test full pipeline
- Use real mock inbox
- Verify end-to-end flow

### UI Tests
- Manual testing via demo video
- Test all user workflows
- Verify error states

## Deployment Options

### Local Development
```bash
streamlit run app.py
```

### Docker Container
```bash
docker build -t email-agent .
docker run -p 8501:8501 email-agent
```

### Cloud Platforms
- **Streamlit Cloud**: Push to GitHub, auto-deploy
- **Heroku**: Use Dockerfile
- **AWS ECS**: Container deployment
- **Azure Web Apps**: Container or Python app
