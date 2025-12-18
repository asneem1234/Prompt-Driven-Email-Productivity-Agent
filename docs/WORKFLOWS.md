# Project Workflows Guide 🔄

This document explains all the workflows in the Prompt-Driven Email Productivity Agent project.

---

## Table of Contents
1. [Email Processing Pipeline](#1-email-processing-pipeline)
2. [RAG-Powered Chat](#2-rag-powered-chat)
3. [Draft Generation](#3-draft-generation)
4. [Prompt Management](#4-prompt-management)
5. [Email Organization](#5-email-organization)
6. [Error Handling](#6-error-handling)

---

## 1. Email Processing Pipeline 📧

### Overview
Every email goes through a 3-step AI-powered pipeline.

### Workflow Diagram
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌─────────────┐
│   INBOX     │ ──► │  CATEGORIZE  │ ──► │   EXTRACT   │ ──► │  SUMMARIZE  │
│  (emails)   │     │   (Step 1)   │     │   ACTIONS   │     │  (Step 3)   │
└─────────────┘     └──────────────┘     │   (Step 2)  │     └─────────────┘
                                         └─────────────┘
                                                │
                                                ▼
                                    ┌─────────────────────┐
                                    │   PROCESSED EMAIL   │
                                    │ - category          │
                                    │ - action_items[]    │
                                    │ - summary           │
                                    └─────────────────────┘
```

### Step-by-Step Process

| Step | Method | What It Does | Temperature |
|------|--------|--------------|-------------|
| 1 | `categorize_email()` | Assigns category (Work, Personal, Urgent, etc.) | 0.3 (precise) |
| 2 | `extract_actions()` | Finds to-do items and deadlines | 0.3 (precise) |
| 3 | `summarize_email()` | Creates TL;DR summary | 0.5 (balanced) |

### Code Flow
```python
# In email_processor.py
def process_email(email):
    processed = initialize_result()
    
    # Step 1: Categorize
    category_result = self.categorize_email(email)
    processed["category"] = category_result["response"]
    
    # Step 2: Extract Actions
    actions_result = self.extract_actions(email)
    processed["action_items"] = actions_result["response"]["action_items"]
    
    # Step 3: Summarize
    summary_result = self.summarize_email(email)
    processed["summary"] = summary_result["response"]
    
    return processed
```

### User Journey
1. User clicks **"Process Emails"** on inbox page
2. System loads emails from `mock_inbox.json`
3. Each email goes through 3-step pipeline
4. Results display with category badges and summaries
5. Action items appear in email details

---

## 2. RAG-Powered Chat 💬

### Overview
Users can ask natural language questions about their emails. RAG (Retrieval-Augmented Generation) finds relevant emails before AI responds.

### Workflow Diagram
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  USER ASKS   │ ──► │  RAG SEARCH  │ ──► │   BUILD      │ ──► │  AI RESPONDS │
│  QUESTION    │     │  (keywords)  │     │   CONTEXT    │     │  (Gemini)    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
        │                   │                    │                    │
        │                   ▼                    ▼                    ▼
        │           "Find emails with"    "Stats + Top 5      "Based on your
        │           matching keywords"     relevant emails"    emails, here's..."
```

### RAG Process
```
User: "What meetings do I have this week?"
                    │
                    ▼
┌─────────────────────────────────────────────┐
│           KEYWORD EXTRACTION                │
│   "meetings" "week" "schedule" "calendar"   │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│           RELEVANCE SCORING                 │
│   Email 1: score 0.8 (has "meeting")        │
│   Email 2: score 0.6 (has "schedule")       │
│   Email 3: score 0.2 (no matches)           │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│           TOP 5 SELECTED                    │
│   → Only most relevant emails sent to AI   │
└─────────────────────────────────────────────┘
```

### Code Flow
```python
# In email_agent.py
def chat(user_message, selected_email=None):
    # 1. RAG retrieval
    relevant_emails = self.rag_system.retrieve(user_message, top_k=5)
    
    # 2. Build context with stats + relevant emails
    context = self._build_rag_context(relevant_emails, selected_email)
    
    # 3. Format prompt
    prompt = self.prompt_manager.format_prompt("chat_response", {...})
    
    # 4. Call LLM
    response = self.llm_client.call_llm(prompt)
    
    return response
```

### Example Conversations
| User Question | RAG Finds | AI Response |
|---------------|-----------|-------------|
| "Emails from John" | All emails where sender contains "John" | Lists John's emails with summaries |
| "What's urgent?" | Emails with "urgent", "ASAP", "deadline" | Prioritized list of urgent items |
| "Meeting tomorrow" | Emails mentioning "meeting" | Meeting details and times |

---

## 3. Draft Generation ✍️

### Overview
AI generates reply drafts that users can edit before saving. **Emails are never sent automatically.**

### Workflow Diagram
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   SELECT     │ ──► │  USER GIVES  │ ──► │  AI DRAFTS   │ ──► │  USER EDITS  │
│   EMAIL      │     │ INSTRUCTIONS │     │   REPLY      │     │   & SAVES    │
└──────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
                                                                      │
                                                                      ▼
                                                            ┌──────────────┐
                                                            │  STORED IN   │
                                                            │ drafts.json  │
                                                            └──────────────┘
```

### Draft Generation Process
```python
# In email_agent.py
def generate_reply(email, user_instructions=""):
    # 1. Get auto_reply prompt template
    prompt = self.prompt_manager.format_prompt("auto_reply", {
        "sender": email["sender"],
        "subject": email["subject"],
        "body": email["body"],
        "user_instructions": user_instructions
    })
    
    # 2. Call LLM
    response = self.llm_client.call_llm(prompt)
    
    # 3. Return structured draft
    return {
        "to": email["sender"],
        "subject": f"Re: {email['subject']}",
        "body": response["response"],
        "original_email_id": email["id"]
    }
```

### Human-in-the-Loop Design
```
┌─────────────────────────────────────────────────────────────┐
│                    SAFETY BY DESIGN                         │
│                                                             │
│   ❌ NO auto-send feature                                   │
│   ❌ NO "Send" button in the app                            │
│   ✅ All drafts require human review                        │
│   ✅ Stored locally in drafts.json                          │
│   ✅ Users must copy/paste to actual email client           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### User Journey
1. Click email to view details
2. Click **"Draft Reply"** button
3. (Optional) Add instructions like "Be formal" or "Decline politely"
4. AI generates draft
5. Edit the draft text
6. Click **"Save Draft"**
7. View saved drafts in Drafts page

---

## 4. Prompt Management 🧠

### Overview
All AI behavior is controlled by editable prompts. Users can modify how the AI categorizes, summarizes, and responds.

### Workflow Diagram
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   DEFAULT    │ ──► │  USER EDITS  │ ──► │  AI BEHAVIOR │
│   PROMPTS    │     │   PROMPT     │     │   CHANGES    │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │                    │
       │                    ▼                    ▼
       │           ┌──────────────┐     "AI now categorizes
       │           │   VERSION    │      emails differently"
       │           │   SAVED      │
       │           └──────────────┘
       │                    │
       ▼                    ▼
┌─────────────────────────────────────┐
│         CAN RESET TO DEFAULT        │
└─────────────────────────────────────┘
```

### Available Prompts
| Prompt Key | Controls | Example Modification |
|------------|----------|---------------------|
| `categorization` | Email categories | Add "Newsletter" category |
| `action_extraction` | What counts as action item | Include deadlines only |
| `summarization` | Summary style | Make summaries shorter |
| `chat_response` | Chat personality | Make AI more formal |
| `auto_reply` | Draft style | Always include signature |

### Prompt Template Structure
```python
{
    "categorization": {
        "template": "Categorize this email...\n\nFrom: {sender}\nSubject: {subject}\nBody: {body}",
        "version": 3,
        "updated_at": "2025-12-18T10:30:00"
    }
}
```

### Code Flow
```python
# In prompt_manager.py

# Get prompt for use
prompt = prompt_manager.format_prompt("categorization", email_data)

# Edit prompt
prompt_manager.update_prompt("categorization", new_template)

# Reset to default
prompt_manager.reset_to_default("categorization")

# Get version history
history = prompt_manager.get_prompt_history("categorization")
```

### User Journey
1. Go to **"Prompt Brain"** page
2. Select prompt to edit (e.g., "categorization")
3. Modify the template text
4. Click **"Save"**
5. Version number increments automatically
6. Process emails to see new behavior
7. (Optional) Reset to default if needed

---

## 5. Email Organization 📂

### Overview
Users can organize emails with stars, snooze, and category filters.

### Organization Actions
```
┌─────────────────────────────────────────────────────────────┐
│                    EMAIL ACTIONS                            │
│                                                             │
│   ⭐ STAR      - Mark as important                          │
│   😴 SNOOZE    - Hide until later                          │
│   🗑️ DELETE    - Remove from inbox                          │
│   📁 FILTER    - View by category                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Data Storage
| Action | Stored In | Format |
|--------|-----------|--------|
| Star | `starred_emails.json` | List of email IDs |
| Snooze | `snoozed_emails.json` | `{email_id: snooze_until_date}` |
| Drafts | `drafts.json` | Full draft objects |
| Sent | `sent_emails.json` | Full sent email objects |

### Category Filter Workflow
```
User clicks "Work" filter
         │
         ▼
┌─────────────────────────────────┐
│  get_emails_by_category("Work") │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Loop through processed_emails  │
│  Return where category == Work  │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Display filtered email list    │
└─────────────────────────────────┘
```

---

## 6. Error Handling 🛡️

### Overview
The system gracefully handles failures without crashing.

### Rate Limit Handling
```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  API CALL    │ ──► │  429 ERROR   │ ──► │  WAIT &      │
│  TO GEMINI   │     │  (rate limit)│     │  RETRY       │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
                                                 ▼
                                    ┌─────────────────────┐
                                    │  Extract retry time │
                                    │  from error message │
                                    │  Wait + 1s buffer   │
                                    │  Try again          │
                                    └─────────────────────┘
```

### Code Example
```python
# In email_processor.py
for attempt in range(max_retries):
    try:
        response = self.fast_model.generate_content(prompt)
        return {"success": True, "response": parsed_response}
    except Exception as e:
        if "429" in str(e):
            # Extract retry delay
            retry_delay = extract_delay(str(e))
            time.sleep(retry_delay + 1)
            continue  # Retry
        else:
            return {"success": False, "error": str(e)}
```

### Pipeline Error Isolation
```
┌─────────────────────────────────────────────────────────────┐
│              ERROR ISOLATION DESIGN                         │
│                                                             │
│   Step 1 (Categorize) ──FAILS──► Log error, continue       │
│                           │                                 │
│   Step 2 (Actions)   ────────► Still runs!                 │
│                           │                                 │
│   Step 3 (Summarize) ────────► Still runs!                 │
│                                                             │
│   Result: Partial data is better than no data               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Error Response Structure
```python
# Success
{
    "success": True,
    "response": {...},
    "model": "gemini-2.5-flash-lite"
}

# Failure
{
    "success": False,
    "response": {"category": "Other", "confidence": 0.0},
    "error": "QUOTA_EXHAUSTED",
    "model": "gemini-2.5-flash-lite"
}
```

---

## Complete System Flow 🔄

### End-to-End User Journey
```
┌─────────────────────────────────────────────────────────────────────────┐
│                         COMPLETE USER JOURNEY                           │
└─────────────────────────────────────────────────────────────────────────┘

1. SETUP
   └── Enter Gemini API key → Saved to session

2. PROCESS INBOX
   └── Click "Process" → 3-step pipeline runs → Results displayed

3. VIEW & ORGANIZE
   └── Browse emails → Star important → Snooze for later

4. CHAT WITH AI
   └── Ask questions → RAG finds context → AI answers

5. DRAFT REPLIES
   └── Select email → Generate draft → Edit → Save

6. CUSTOMIZE AI
   └── Edit prompts → Change AI behavior → See results

```

### Data Flow Architecture
```
┌──────────────┐
│   USER       │
│   BROWSER    │
└──────┬───────┘
       │ HTTP
       ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   FLASK      │ ──► │   EMAIL      │ ──► │   GEMINI     │
│   APP.PY     │     │   AGENT      │     │   API        │
└──────────────┘     └──────────────┘     └──────────────┘
       │                    │
       │                    ▼
       │            ┌──────────────┐
       │            │   RAG        │
       │            │   SYSTEM     │
       │            └──────────────┘
       │
       ▼
┌──────────────┐
│   JSON       │
│   DATA       │
│   FILES      │
└──────────────┘
```

---

## Summary Table

| Workflow | Entry Point | Key Classes | Output |
|----------|-------------|-------------|--------|
| Email Processing | `/process` route | `EmailProcessor` | Categorized emails |
| RAG Chat | `/chat` route | `EmailAgent`, `RAGSystem` | AI responses |
| Draft Generation | `/draft_reply` route | `EmailAgent`, `DraftManager` | Saved drafts |
| Prompt Management | `/prompt_brain` route | `PromptManager` | Updated prompts |
| Organization | Various routes | Flask routes | JSON file updates |
| Error Handling | Throughout | All classes | Graceful failures |

---

*This document provides a complete overview of all workflows in the Email Productivity Agent project.*
