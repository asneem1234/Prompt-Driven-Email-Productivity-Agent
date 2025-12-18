# 📧 System Design Document
## Prompt-Driven Email Productivity Agent

---

## 📋 Table of Contents

1. [System Overview](#1-system-overview)
2. [Architecture Diagram](#2-architecture-diagram)
3. [Technology Stack](#3-technology-stack)
4. [Component Design](#4-component-design)
5. [Data Flow](#5-data-flow)
6. [File Structure](#6-file-structure)
7. [API Endpoints](#7-api-endpoints)
8. [Database Schema](#8-database-schema)
9. [Sequence Diagrams](#9-sequence-diagrams)
10. [Deployment Architecture](#10-deployment-architecture)

---

## 1. System Overview

### 1.1 Purpose
The Prompt-Driven Email Productivity Agent is an AI-powered email management system that helps users:
- **Categorize emails** automatically using AI (Urgent, Deadline, Conversation, Spam, Other)
- **Extract action items** and deadlines from emails
- **Generate draft replies** using customizable AI prompts
- **Chat with inbox** using natural language queries (RAG-powered)
- **Manage prompts** through a "Prompt Brain" interface

### 1.2 Key Design Principles
| Principle | Description |
|-----------|-------------|
| **Safety First** | AI only creates drafts, never auto-sends emails |
| **Prompt-Driven** | All AI behaviors are controlled by editable prompts |
| **Session-Based** | Each user gets isolated state via Flask sessions |
| **Lightweight RAG** | Keyword-based semantic search without external models |
| **Rate Limit Resilient** | Exponential backoff for API rate limits |

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Inbox     │  │   Chat      │  │   Drafts    │  │   Prompt Brain      │ │
│  │   Page      │  │   Page      │  │   Page      │  │   (Config)          │ │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
│         │                │                │                     │            │
│         └────────────────┴────────────────┴─────────────────────┘            │
│                                    │                                          │
│                         HTML/CSS + JavaScript                                 │
└────────────────────────────────────┼──────────────────────────────────────────┘
                                     │ HTTP/AJAX
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            WEB SERVER LAYER                                  │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         Flask Application (app.py)                      │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐  │ │
│  │  │  Routes      │  │  Session     │  │  Template    │  │  Static    │  │ │
│  │  │  /inbox      │  │  Manager     │  │  Renderer    │  │  Files     │  │ │
│  │  │  /chat       │  │              │  │  (Jinja2)    │  │  (CSS)     │  │ │
│  │  │  /api/*      │  │              │  │              │  │            │  │ │
│  │  └──────┬───────┘  └──────────────┘  └──────────────┘  └────────────┘  │ │
│  └─────────┼──────────────────────────────────────────────────────────────┘ │
│            │                                                                 │
└────────────┼─────────────────────────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          BUSINESS LOGIC LAYER (src/)                         │
│                                                                              │
│  ┌────────────────┐   ┌────────────────┐   ┌────────────────────────────┐   │
│  │  EmailAgent    │   │ EmailProcessor │   │     DraftManager           │   │
│  │  ─────────────  │   │  ─────────────  │   │  ───────────────────────  │   │
│  │  • query()     │   │  • process()   │   │  • generate_reply_draft() │   │
│  │  • chat RAG    │   │  • categorize()│   │  • generate_new_draft()   │   │
│  │  • gen reply   │   │  • extract()   │   │  • save/delete/export()   │   │
│  └───────┬────────┘   └───────┬────────┘   └──────────────┬─────────────┘   │
│          │                    │                           │                  │
│          └──────────┬─────────┴───────────────────────────┘                  │
│                     │                                                        │
│          ┌──────────┴──────────┐                                             │
│          ▼                     ▼                                             │
│  ┌────────────────┐   ┌────────────────┐   ┌──────────────────────────────┐ │
│  │   RAGSystem    │   │ PromptManager  │   │         LLMClient            │ │
│  │  ─────────────  │   │  ─────────────  │   │  ─────────────────────────  │ │
│  │  • index()     │   │  • load/save() │   │  • call_llm()               │ │
│  │  • retrieve()  │   │  • format()    │   │  • retry logic              │ │
│  │  • similarity  │   │  • update()    │   │  • JSON parsing             │ │
│  └────────────────┘   └───────┬────────┘   └──────────────┬───────────────┘ │
│                               │                           │                  │
└───────────────────────────────┼───────────────────────────┼──────────────────┘
                                │                           │
                                ▼                           ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA LAYER                                        │
│                                                                              │
│  ┌─────────────────────────────────┐    ┌────────────────────────────────┐  │
│  │         JSON Files (data/)       │    │      External API              │  │
│  │  ┌───────────────────────────┐  │    │  ┌──────────────────────────┐  │  │
│  │  │  mock_inbox.json          │  │    │  │   Google Gemini API      │  │  │
│  │  │  drafts.json              │  │    │  │   (gemini-2.5-flash-lite)     │  │  │
│  │  │  default_prompts.json     │  │    │  │                          │  │  │
│  │  │  starred_emails.json      │  │    │  │   Rate: 15 req/min       │  │  │
│  │  │  snoozed_emails.json      │  │    │  │   Tokens: 1000 max       │  │  │
│  │  │  sent_emails.json         │  │    │  └──────────────────────────┘  │  │
│  │  └───────────────────────────┘  │    │                                │  │
│  └─────────────────────────────────┘    └────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Technology Stack

### 3.1 Backend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Web Framework | Flask 3.0 | HTTP server, routing, sessions |
| AI Model | Google Gemini 2.5 Flash Lite | Email categorization, replies, chat |
| Template Engine | Jinja2 | HTML rendering |
| Environment | python-dotenv | API key management |
| Math Operations | NumPy 1.24 | Vector operations for RAG |

### 3.2 Frontend
| Component | Technology | Purpose |
|-----------|------------|---------|
| Styling | Custom CSS | Gmail-like UI |
| Icons | Material Icons | Google-style iconography |
| Fonts | Google Sans, Roboto | Typography |
| Interactivity | Vanilla JavaScript | AJAX calls, DOM manipulation |

### 3.3 Data Storage
| Type | Format | Location |
|------|--------|----------|
| Emails | JSON | `data/mock_inbox.json` |
| Drafts | JSON | `data/drafts.json` |
| Prompts | JSON | `data/default_prompts.json` |
| Session State | In-Memory | Flask session |

---

## 4. Component Design

### 4.1 LLMClient (`src/llm_client.py`)
**Purpose:** Wrapper for all Gemini AI API interactions.

```
┌─────────────────────────────────────────┐
│              LLMClient                  │
├─────────────────────────────────────────┤
│  - api_key: str                         │
│  - model: GenerativeModel               │
│  - call_history: List[Dict]             │
├─────────────────────────────────────────┤
│  + __init__(model="gemini-2.5-flash-lite")   │
│  + call_llm(prompt, temp, tokens, json) │
│  + get_call_history()                   │
│  + clear_history()                      │
└─────────────────────────────────────────┘
```

**Key Features:**
- Automatic JSON response parsing
- Exponential backoff for rate limits (10s → 20s → 40s)
- Safety filter detection
- Call history logging

---

### 4.2 PromptManager (`src/prompt_manager.py`)
**Purpose:** Manages reusable AI prompt templates.

```
┌─────────────────────────────────────────┐
│            PromptManager                │
├─────────────────────────────────────────┤
│  - prompts: Dict[str, Dict]             │
│  - prompts_file: str                    │
│  - prompt_history: List                 │
│  - read_only: bool                      │
├─────────────────────────────────────────┤
│  + load_prompts()                       │
│  + save_prompts()                       │
│  + get_prompt(type)                     │
│  + update_prompt(type, data)            │
│  + format_prompt(type, email_data)      │
└─────────────────────────────────────────┘
```

**Prompt Types:**
| Type | Purpose | Placeholders |
|------|---------|--------------|
| `categorization` | Classify emails | `{sender}`, `{subject}`, `{body}` |
| `action_extraction` | Extract tasks | `{sender}`, `{subject}`, `{body}` |
| `auto_reply` | Generate replies | `{sender}`, `{subject}`, `{body}` |
| `summarization` | Summarize emails | `{sender}`, `{subject}`, `{body}` |

---

### 4.3 EmailProcessor (`src/email_processor.py`)
**Purpose:** Processes emails through the AI pipeline.

```
┌─────────────────────────────────────────┐
│           EmailProcessor                │
├─────────────────────────────────────────┤
│  - llm_client: LLMClient                │
│  - prompt_manager: PromptManager        │
│  - processed_emails: Dict               │
│  - fast_model: GenerativeModel          │
├─────────────────────────────────────────┤
│  + process_email(email) → processed     │
│  + categorize_email(email) → category   │
│  + extract_actions(email) → actions     │
│  + summarize_email(email) → summary     │
│  + get_emails_by_category(cat)          │
│  + get_all_action_items()               │
└─────────────────────────────────────────┘
```

**Processing Pipeline:**
```
Email Input
    │
    ├──→ [1] Categorize → Urgent/Deadline/Conversation/Spam/Other
    │
    ├──→ [2] Extract Actions → Task list with deadlines
    │
    └──→ [3] Summarize → Key points + urgency level
    │
    ▼
Processed Email Output
```

---

### 4.4 EmailRAGSystem (`src/rag_system.py`)
**Purpose:** Semantic search for finding relevant emails.

```
┌─────────────────────────────────────────┐
│           EmailRAGSystem                │
├─────────────────────────────────────────┤
│  - emails: List[Dict]                   │
│  - email_embeddings: Dict               │
│  - indexed: bool                        │
├─────────────────────────────────────────┤
│  + index_emails(emails)                 │
│  + retrieve_relevant_emails(query, k)   │
│  + search_by_sender(sender)             │
│  + search_by_keywords(keywords)         │
│  + get_unread_emails()                  │
│  + get_stats()                          │
└─────────────────────────────────────────┘
```

**RAG Algorithm (Lightweight):**
```
Query: "urgent meeting"
         │
         ▼
┌─────────────────────────┐
│ 1. Create Query Embedding│
│    (keyword frequencies) │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 2. Calculate Similarity │
│    (cosine similarity)  │
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 3. Apply Keyword Boost  │
│    (1.5x if exact match)│
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ 4. Return Top-K Results │
└─────────────────────────┘
```

---

### 4.5 EmailAgent (`src/email_agent.py`)
**Purpose:** Conversational chat interface using RAG.

```
┌─────────────────────────────────────────┐
│             EmailAgent                  │
├─────────────────────────────────────────┤
│  - llm_client: LLMClient                │
│  - email_processor: EmailProcessor      │
│  - rag_system: EmailRAGSystem           │
│  - prompt_manager: PromptManager        │
│  - conversation_history: List           │
├─────────────────────────────────────────┤
│  + query(user_query, email, context)    │
│  + generate_reply(email, instruction)   │
│  + _build_rag_context(query, emails)    │
│  + get_conversation_history()           │
└─────────────────────────────────────────┘
```

**Chat Capabilities:**
- 📧 Email parsing and analysis
- 📋 Information extraction (dates, names, amounts)
- 📝 Content summarization
- 😊 Sentiment analysis
- 🏷️ Email categorization
- 💬 Smart response suggestions

---

### 4.6 DraftManager (`src/draft_manager.py`)
**Purpose:** Generates and stores email drafts (never sends).

```
┌─────────────────────────────────────────┐
│            DraftManager                 │
├─────────────────────────────────────────┤
│  - llm_client: LLMClient                │
│  - prompt_manager: PromptManager        │
│  - drafts: Dict[str, Dict]              │
│  - drafts_file: str                     │
├─────────────────────────────────────────┤
│  + generate_reply_draft(email, instr)   │
│  + generate_new_email_draft(to, subj)   │
│  + get_draft(id)                        │
│  + get_all_drafts()                     │
│  + update_draft(id, updates)            │
│  + delete_draft(id)                     │
│  + export_draft_as_text(id)             │
└─────────────────────────────────────────┘
```

---

## 5. Data Flow

### 5.1 Email Categorization Flow
```
┌──────────┐    ┌──────────┐    ┌───────────────┐    ┌──────────┐    ┌──────────┐
│  User    │───▶│  Flask   │───▶│EmailProcessor │───▶│LLMClient │───▶│ Gemini   │
│  Click   │    │  /api/   │    │ categorize()  │    │call_llm()│    │   API    │
│"Process" │    │categorize│    │               │    │          │    │          │
└──────────┘    └──────────┘    └───────────────┘    └──────────┘    └──────────┘
                                       │                                   │
                                       │◀──────────────────────────────────┘
                                       │         JSON Response
                                       ▼
                              ┌───────────────────┐
                              │ {                 │
                              │   "category":     │
                              │     "Urgent",     │
                              │   "confidence":   │
                              │     0.95,         │
                              │   "reasoning":    │
                              │     "..."         │
                              │ }                 │
                              └───────────────────┘
```

### 5.2 Chat Query Flow (RAG)
```
┌──────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐
│ User     │───▶│  Flask   │───▶│EmailAgent  │───▶│RAGSystem │
│ "Show    │    │ /api/    │    │  query()   │    │retrieve()│
│  urgent" │    │  chat    │    │            │    │          │
└──────────┘    └──────────┘    └────────────┘    └──────────┘
                                      │                │
                                      │◀───────────────┘
                                      │   Top 5 Relevant Emails
                                      ▼
                               ┌─────────────┐
                               │ Build RAG   │
                               │  Context    │
                               └──────┬──────┘
                                      │
                                      ▼
                               ┌─────────────┐    ┌──────────┐
                               │ LLMClient   │───▶│ Gemini   │
                               │  call_llm() │    │   API    │
                               └──────┬──────┘    └──────────┘
                                      │
                                      ▼
                               ┌─────────────────────┐
                               │ Formatted Response  │
                               │ with email refs     │
                               └─────────────────────┘
```

---

## 6. File Structure

```
Prompt-Driven-Email-Productivity-Agent/
│
├── 📄 app.py                    # Flask application (671 lines)
│   ├── Routes: /, /inbox, /chat, /drafts, /prompt-brain
│   ├── API: /api/chat, /api/categorize-all, /api/generate-reply
│   └── Session management, template rendering
│
├── 📁 src/                      # Core business logic
│   ├── __init__.py              # Package initializer
│   ├── llm_client.py            # Gemini API wrapper (169 lines)
│   ├── prompt_manager.py        # Prompt template manager (130 lines)
│   ├── email_processor.py       # Email processing pipeline (216 lines)
│   ├── email_agent.py           # Chat agent with RAG (307 lines)
│   ├── rag_system.py            # Semantic search system (247 lines)
│   └── draft_manager.py         # Draft generation/storage (217 lines)
│
├── 📁 templates/                # Jinja2 HTML templates
│   ├── base.html                # Base layout (435 lines) - Gmail-style UI
│   ├── inbox.html               # Email list view
│   ├── chat.html                # Chat interface
│   ├── drafts.html              # Drafts management
│   ├── prompt_brain.html        # Prompt configuration
│   ├── folder.html              # Folder view (starred, sent, etc.)
│   └── setup.html               # API key setup
│
├── 📁 static/
│   └── style.css                # Gmail-inspired styling
│
├── 📁 data/                     # JSON data storage
│   ├── mock_inbox.json          # 25 sample emails (328 lines)
│   ├── default_prompts.json     # 4 prompt templates
│   ├── drafts.json              # Saved drafts
│   ├── starred_emails.json      # Starred emails
│   ├── snoozed_emails.json      # Snoozed emails
│   ├── sent_emails.json         # Sent emails
│   └── generate_emails.py       # Script to generate test emails
│
├── 📁 docs/                     # Documentation
│   ├── ARCHITECTURE.md          # Architecture overview
│   ├── PROJECT_STRUCTURE.md     # File structure details
│   ├── QUICKSTART.md            # Getting started guide
│   └── SYSTEM_DESIGN.md         # This document
│
├── 📄 requirements.txt          # Python dependencies
├── 📄 Dockerfile                # Docker configuration
├── 📄 vercel.json               # Vercel deployment config
├── 📄 run.bat                   # Windows run script
├── 📄 run.sh                    # Unix run script
└── 📄 README.md                 # Project documentation
```

---

## 7. API Endpoints

### 7.1 Page Routes
| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Redirect to inbox |
| `/inbox` | GET | Main email list view |
| `/chat` | GET | Chat interface |
| `/drafts` | GET | Drafts management |
| `/prompt-brain` | GET | Prompt configuration |
| `/starred` | GET | Starred emails |
| `/snoozed` | GET | Snoozed emails |
| `/sent` | GET | Sent emails |
| `/setup` | GET/POST | API key setup |

### 7.2 API Endpoints
| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/api/load-inbox` | POST | - | `{success, count}` |
| `/api/categorize-all` | POST | - | `{success, processed, failed}` |
| `/api/process-email/<id>` | POST | - | `{success, result}` |
| `/api/select-email/<id>` | POST | - | `{success}` |
| `/api/chat` | POST | `{query}` | `{success, response}` |
| `/api/generate-reply` | POST | `{email_id, instruction}` | `{success, reply_body}` |
| `/api/save-draft` | POST | `{to, subject, body}` | `{success, draft}` |
| `/api/delete-draft/<id>` | DELETE | - | `{success}` |
| `/api/update-prompt` | POST | `{type, prompt}` | `{success}` |
| `/api/test-prompt` | POST | `{prompt, email_id}` | `{success, response}` |

---

## 8. Database Schema

### 8.1 Email Object (`mock_inbox.json`)
```json
{
  "id": "e001",
  "sender": "chris.lee@solutions.com",
  "sender_name": "Chris Lee",
  "subject": "Project Update - Week 47",
  "timestamp": "2025-11-10T18:44:12.428802Z",
  "body": "Hello, attached is the document...",
  "thread_id": "thread_001",
  "read": false,
  "starred": false,
  "important": false,
  "folder": "inbox"
}
```

### 8.2 Draft Object (`drafts.json`)
```json
{
  "id": "draft_20251218_143022",
  "created_at": "2025-12-18T14:30:22.123456",
  "type": "reply",
  "original_email_id": "e001",
  "in_reply_to": {
    "sender": "chris.lee@solutions.com",
    "subject": "Project Update - Week 47"
  },
  "draft_content": {
    "subject": "Re: Project Update - Week 47",
    "body": "Hi Chris, thank you for the update...",
    "tone": "professional",
    "suggested_actions": ["Schedule follow-up meeting"]
  },
  "prompt_used": "Generate a reply...",
  "status": "draft"
}
```

### 8.3 Prompt Object (`default_prompts.json`)
```json
{
  "categorization": {
    "name": "Email Categorization",
    "prompt": "You are an email categorization assistant...",
    "description": "Categorizes emails with color-coded categories"
  }
}
```

---

## 9. Sequence Diagrams

### 9.1 Email Categorization Sequence
```
User          Flask           EmailProcessor     LLMClient         Gemini API
 │               │                   │               │                  │
 │──Click───────▶│                   │               │                  │
 │ "Categorize"  │                   │               │                  │
 │               │──categorize_all()─▶│               │                  │
 │               │                   │               │                  │
 │               │                   │ Loop for each email              │
 │               │                   ├───────────────────────────────────┤
 │               │                   │──categorize_email()─▶│           │
 │               │                   │                      │           │
 │               │                   │──format_prompt()────▶│           │
 │               │                   │                      │           │
 │               │                   │                      │──call()──▶│
 │               │                   │                      │           │
 │               │                   │                      │◀──JSON────│
 │               │                   │◀─────result──────────│           │
 │               │                   │                      │           │
 │               │                   │──sleep(4s)───────────│  Rate     │
 │               │                   │                      │  Limit    │
 │               │                   ├───────────────────────────────────┤
 │               │                   │               │                  │
 │               │◀──{processed}─────│               │                  │
 │◀──Update UI───│                   │               │                  │
 │               │                   │               │                  │
```

### 9.2 RAG Chat Query Sequence
```
User          Flask         EmailAgent      RAGSystem       LLMClient      Gemini
 │               │               │               │               │            │
 │──"Show urgent"▶│               │               │               │            │
 │               │──query()─────▶│               │               │            │
 │               │               │               │               │            │
 │               │               │──retrieve()──▶│               │            │
 │               │               │               │               │            │
 │               │               │               │──similarity───│            │
 │               │               │               │   calculation │            │
 │               │               │               │               │            │
 │               │               │◀──top 5 emails│               │            │
 │               │               │               │               │            │
 │               │               │──build_context()──────────────│            │
 │               │               │               │               │            │
 │               │               │──────────────────call_llm()──▶│            │
 │               │               │               │               │──prompt()─▶│
 │               │               │               │               │            │
 │               │               │               │               │◀──answer───│
 │               │               │◀──────────────────result──────│            │
 │               │◀──response────│               │               │            │
 │◀──Display─────│               │               │               │            │
```

---

## 10. Deployment Architecture

### 10.1 Local Development
```
┌─────────────────────────────────────────┐
│            Developer Machine            │
│  ┌─────────────────────────────────────┐│
│  │  Flask Dev Server (port 5000)       ││
│  │  ┌─────────────────────────────────┐││
│  │  │  app.py (debug=True)            │││
│  │  └─────────────────────────────────┘││
│  └─────────────────────────────────────┘│
│                    │                    │
│                    ▼                    │
│  ┌─────────────────────────────────────┐│
│  │  .env file                          ││
│  │  GEMINI_API_KEY=your_key            ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
           │
           ▼ HTTPS
┌─────────────────────────────────────────┐
│         Google Gemini API               │
│         models.inference.ai             │
└─────────────────────────────────────────┘
```

### 10.2 Docker Deployment
```
┌─────────────────────────────────────────┐
│            Docker Container             │
│  ┌─────────────────────────────────────┐│
│  │  Python 3.11-slim                   ││
│  │  ┌─────────────────────────────────┐││
│  │  │  Flask App                      │││
│  │  │  Port: 8501 (exposed)           │││
│  │  └─────────────────────────────────┘││
│  │  ┌─────────────────────────────────┐││
│  │  │  /app (working directory)       │││
│  │  │  ├── app.py                     │││
│  │  │  ├── src/                       │││
│  │  │  └── data/                      │││
│  │  └─────────────────────────────────┘││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### 10.3 Vercel Serverless Deployment
```
┌─────────────────────────────────────────┐
│              Vercel Edge                │
│  ┌─────────────────────────────────────┐│
│  │  Serverless Function                ││
│  │  ┌─────────────────────────────────┐││
│  │  │  app.py                         │││
│  │  │  application = app (WSGI)       │││
│  │  └─────────────────────────────────┘││
│  └─────────────────────────────────────┘│
│                                         │
│  ⚠️ Limitations:                        │
│  - Read-only filesystem                 │
│  - Prompts stored in-memory only        │
│  - Session data ephemeral               │
└─────────────────────────────────────────┘
```

---

## 11. Security Considerations

| Concern | Mitigation |
|---------|------------|
| API Key Exposure | Stored in `.env`, never committed to git |
| Session Hijacking | Random secret key via `os.urandom(24)` |
| XSS Attacks | Jinja2 auto-escaping enabled |
| Rate Limiting | Exponential backoff (10s → 20s → 40s) |
| AI Safety | Google's safety filters + response validation |
| Data Privacy | No real emails - mock data only |

---

## 12. Performance Optimizations

| Optimization | Implementation |
|--------------|----------------|
| Fast Categorization | Separate `gemini-2.5-flash-lite` model for bulk processing |
| Rate Limit Protection | 4-second delay between API calls |
| Lazy Loading | RAG indexes only when first query is made |
| Response Caching | Processed emails stored in memory |
| Minimal Dependencies | Only 4 Python packages required |

---

## 13. Future Enhancements

- [ ] Real email integration (IMAP/SMTP)
- [ ] User authentication
- [ ] Database persistence (PostgreSQL)
- [ ] Email threading visualization
- [ ] Custom category colors
- [ ] Scheduled email processing
- [ ] Multi-language support
- [ ] Advanced analytics dashboard

---

*Document Version: 1.0*  
*Last Updated: December 18, 2025*
