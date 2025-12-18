# 🚀 App.py - Main Application Explained

> **File:** `app.py`  
> **Purpose:** Flask web application - the main entry point  
> **Lines:** 671

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [Imports](#2-imports)
3. [App Initialization](#3-app-initialization)
4. [Session Management](#4-session-management-get_or_create_instances)
5. [Page Routes](#5-page-routes)
6. [API Endpoints](#6-api-endpoints)
7. [Helper Functions](#7-helper-functions)
8. [Application Entry Point](#8-application-entry-point)

---

## 1. Overview

This is the **main Flask application** that:
- 🌐 Serves the web interface (HTML pages)
- 🔌 Provides REST API endpoints
- 📧 Manages email processing and AI interactions
- 💬 Handles the chat agent
- 📝 Manages email drafts

```
┌─────────────────────────────────────────────────────────────────┐
│                         app.py                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────┐  │
│  │   Page Routes    │  │   API Routes     │  │   Helpers     │  │
│  ├──────────────────┤  ├──────────────────┤  ├───────────────┤  │
│  │ /               │  │ /api/chat        │  │ format_response│  │
│  │ /inbox          │  │ /api/process-all │  │ get_or_create_ │  │
│  │ /starred        │  │ /api/categorize  │  │   instances()  │  │
│  │ /snoozed        │  │ /api/save-draft  │  │               │  │
│  │ /sent           │  │ /api/generate-   │  │               │  │
│  │ /drafts         │  │      reply       │  │               │  │
│  │ /chat           │  │                  │  │               │  │
│  │ /prompt-brain   │  │                  │  │               │  │
│  └──────────────────┘  └──────────────────┘  └───────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Imports

```python
"""
Flask UI for Email Productivity Agent
Main application interface
"""
```
> Module docstring describing the file.

---

```python
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
```
> **Flask imports:**
> - `Flask` = the web framework
> - `render_template` = render HTML templates
> - `request` = access incoming request data
> - `jsonify` = convert Python dict to JSON response
> - `session` = store user session data
> - `redirect`, `url_for` = navigation helpers

---

```python
import json
```
> `json` for reading/writing JSON files (inbox, drafts, etc.)

---

```python
import os
```
> `os` for environment variables and file operations

---

```python
import time
```
> `time` for delays and timestamps

---

```python
from datetime import datetime
```
> `datetime` for timestamp generation

---

```python
from dotenv import load_dotenv
```
> `load_dotenv` loads variables from `.env` file

---

```python
from src.llm_client import LLMClient
from src.prompt_manager import PromptManager
from src.email_processor import EmailProcessor
from src.draft_manager import DraftManager
from src.email_agent import EmailAgent
```
> Import all custom modules from the `src/` folder:
> - `LLMClient` = Gemini AI wrapper
> - `PromptManager` = prompt template management
> - `EmailProcessor` = email categorization pipeline
> - `DraftManager` = draft creation and storage
> - `EmailAgent` = RAG-powered chat agent

---

## 3. App Initialization

```python
load_dotenv()
```
> Load environment variables from `.env` file.
> Makes `GEMINI_API_KEY` available via `os.environ`.

---

```python
app = Flask(__name__)
```
> Create the Flask application instance.
> `__name__` tells Flask where to find templates and static files.

---

```python
app.secret_key = os.urandom(24)
```
> Generate a random secret key for session encryption.
> `os.urandom(24)` = 24 random bytes.
> ⚠️ This regenerates on each restart (sessions lost on restart).

---

```python
app_instances = {}
```
> Global dictionary to store per-session instances.
> Each user gets their own set of components.

---

## 4. Session Management (get_or_create_instances)

This function manages **per-user state** across requests.

```python
def get_or_create_instances():
    """Get or create application instances for the current session"""
    session_id = session.get('session_id')
```
> Get the current user's session ID from Flask session.

---

```python
    if not session_id:
        session_id = os.urandom(16).hex()
        session['session_id'] = session_id
```
> If no session ID exists, generate a new random one.
> `.hex()` converts bytes to a hex string.

---

```python
    if session_id not in app_instances:
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if api_key:
```
> If this session hasn't been initialized yet, check for API key.

---

```python
            app_instances[session_id] = {
                'llm_client': LLMClient(),
                'prompt_manager': PromptManager(),
                'initialized': True,
                'inbox': [],
                'processed_emails': {},
                'selected_email': None,
                'chat_history': []
            }
```
> Create all the components for this user:
> - `llm_client` = AI client
> - `prompt_manager` = prompt templates
> - `inbox` = list of emails
> - `processed_emails` = categorization results
> - `chat_history` = conversation history

---

```python
            instances = app_instances[session_id]
            instances['email_processor'] = EmailProcessor(
                instances['llm_client'],
                instances['prompt_manager']
            )
```
> Create `EmailProcessor` with dependencies.

---

```python
            instances['draft_manager'] = DraftManager(
                instances['llm_client'],
                instances['prompt_manager']
            )
```
> Create `DraftManager` with dependencies.

---

```python
            instances['email_agent'] = EmailAgent(
                instances['llm_client'],
                instances['email_processor'],
                instances['prompt_manager']
            )
```
> Create `EmailAgent` with dependencies.

---

```python
            # Auto-load inbox from mock data
            inbox_file = "data/mock_inbox.json"
            if os.path.exists(inbox_file):
                with open(inbox_file, 'r', encoding='utf-8') as f:
                    instances['inbox'] = json.load(f)
```
> Automatically load the mock inbox on first request.

---

```python
                # Index emails in RAG system immediately
                instances['email_agent'].rag_system.index_emails(instances['inbox'])
                print(f"🔍 RAG System initialized with {len(instances['inbox'])} emails")
```
> Index all emails in the RAG system for semantic search.

---

```python
    return app_instances[session_id]
```
> Return the instances for this session.

---

## 5. Page Routes

### Home Page (/)

```python
@app.route('/')
def index():
    """Home page - redirect to inbox"""
    return redirect(url_for('inbox'))
```
> Redirect root URL to inbox page.
> `url_for('inbox')` generates the URL for the `inbox` function.

---

### Setup Page (/setup)

```python
@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Setup page for API key"""
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        if api_key:
            os.environ['GEMINI_API_KEY'] = api_key
            # Reset session to reinitialize
            session_id = session.get('session_id')
            if session_id and session_id in app_instances:
                del app_instances[session_id]
            return redirect(url_for('index'))
    
    return render_template('setup.html')
```
> - `GET` = show the setup form
> - `POST` = save the API key and restart session

---

### Inbox Page (/inbox)

```python
@app.route('/inbox')
def inbox():
    """Inbox page"""
    instances = get_or_create_instances()
    
    # Get filter and sort parameters
    filter_category = request.args.get('category', 'All')
    sort_by = request.args.get('sort', 'date_newest')
```
> Get query parameters for filtering:
> - `?category=Work` filters by category
> - `?sort=date_newest` sorts by date

---

```python
    # Filter emails
    emails = instances['inbox']
    filtered_emails = []
    
    for email in emails:
        email_id = email['id']
        processed = instances['processed_emails'].get(email_id, {})
        
        # Apply category filter
        if filter_category != 'All':
            cat = processed.get('category', {}).get('category', 'Unknown')
            if cat != filter_category:
                continue
        
        # Attach processed data
        email['processed'] = processed
        filtered_emails.append(email)
```
> Filter emails by category and attach processing results.

---

```python
    # Calculate stats
    stats = {
        'total': len(instances['inbox']),
        'processed': len(instances['processed_emails']),
        'categories': {}
    }
    
    for processed in instances['processed_emails'].values():
        if processed and isinstance(processed, dict):
            category_data = processed.get('category', {})
            if category_data and isinstance(category_data, dict):
                cat = category_data.get('category', 'Unknown')
                stats['categories'][cat] = stats['categories'].get(cat, 0) + 1
```
> Calculate statistics for the sidebar.

---

```python
    return render_template('inbox.html', 
                         emails=filtered_emails, 
                         stats=stats,
                         filter_category=filter_category,
                         selected_email=instances.get('selected_email'))
```
> Render the inbox template with all the data.

---

### Folder Pages

```python
@app.route('/starred')
def starred():
    """Starred emails page"""
    starred_file = "data/starred_emails.json"
    emails = []
    if os.path.exists(starred_file):
        with open(starred_file, 'r', encoding='utf-8') as f:
            emails = json.load(f)
    return render_template('folder.html', 
                         emails=emails, 
                         folder_name='Starred',
                         folder_icon='star',
                         folder_color='#f9ab00',
                         is_sent=False)
```
> Load starred emails from JSON and render folder template.
> Same pattern for `/snoozed` and `/sent`.

---

### Chat Page (/chat)

```python
@app.route('/chat')
def chat():
    """Email agent chat page"""
    instances = get_or_create_instances()
    
    return render_template('chat.html', chat_history=instances['chat_history'])
```
> Render chat page with conversation history.

---

### Prompt Brain Page (/prompt-brain)

```python
@app.route('/prompt-brain')
def prompt_brain():
    """Prompt brain configuration page"""
    instances = get_or_create_instances()
    
    prompt_manager = instances['prompt_manager']
    all_prompts = prompt_manager.get_all_prompts()
    
    selected_type = request.args.get('type', list(all_prompts.keys())[0] if all_prompts else None)
    
    return render_template('prompt_brain.html', 
                         prompts=all_prompts,
                         selected_type=selected_type,
                         inbox=instances['inbox'][:5])
```
> Render prompt editing page with all prompts and sample emails.

---

### Drafts Page (/drafts)

```python
@app.route('/drafts')
def drafts():
    """Drafts page"""
    instances = get_or_create_instances()
    
    # Get drafts from draft_manager
    draft_manager = instances['draft_manager']
    manager_drafts = draft_manager.get_all_drafts()
    
    # Also get drafts from session (generated replies)
    session_drafts = instances.get('drafts', [])
    
    # Combine and sort
    all_drafts = list(manager_drafts) + list(session_drafts)
    all_drafts = sorted(all_drafts, key=lambda d: d.get('created_at', d.get('timestamp', '')), reverse=True)
    
    return render_template('drafts.html', drafts=all_drafts)
```
> Combine drafts from `DraftManager` and session, sort by date.

---

## 6. API Endpoints

### POST /api/load-inbox

```python
@app.route('/api/load-inbox', methods=['POST'])
def load_inbox():
    """Load mock inbox from JSON file"""
    instances = get_or_create_instances()
    inbox_file = "data/mock_inbox.json"
    
    try:
        if os.path.exists(inbox_file):
            with open(inbox_file, 'r', encoding='utf-8') as f:
                instances['inbox'] = json.load(f)
            return jsonify({'success': True, 'count': len(instances['inbox'])})
        else:
            return jsonify({'success': False, 'error': 'Mock inbox file not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```
> Load emails from JSON file into session.

---

### POST /api/categorize-all

```python
@app.route('/api/categorize-all', methods=['POST'])
def categorize_all():
    """Categorize all emails with color-coded categories"""
    instances = get_or_create_instances()
    
    try:
        processed_count = 0
        failed_count = 0
        total_emails = len(instances['inbox'])
        
        for idx, email in enumerate(instances['inbox'], 1):
            try:
                print(f"📧 [{idx}/{total_emails}] Categorizing email {email['id']}")
                
                # Call categorize directly
                category_result = instances['email_processor'].categorize_email(email)
```
> Loop through all emails and categorize each one.

---

```python
                if category_result.get('success'):
                    processed = {
                        'email': email,
                        'category': category_result.get('response'),
                        'processed_at': datetime.now().isoformat()
                    }
                    instances['processed_emails'][email['id']] = processed
                    email['processed'] = processed
                    processed_count += 1
```
> Store successful categorization results.

---

```python
                else:
                    failed_count += 1
                    error_msg = category_result.get('error', 'Unknown error')
                    
                    # Stop immediately if daily quota is exhausted
                    if error_msg == "QUOTA_EXHAUSTED":
                        return jsonify({
                            'success': False,
                            'processed': processed_count,
                            'failed': failed_count,
                            'error': 'Daily API quota exhausted.'
                        })
```
> Handle errors, especially API quota limits.

---

```python
                # Delay to stay under requests/minute limit
                time.sleep(4)
```
> 4-second delay between API calls to avoid rate limits.

---

### POST /api/chat

```python
@app.route('/api/chat', methods=['POST'])
def chat_query():
    """Handle chat query"""
    instances = get_or_create_instances()
    
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'success': False, 'error': 'No query provided'})
    
    try:
        result = instances['email_agent'].query(
            query,
            selected_email=instances.get('selected_email'),
            context_emails=instances['inbox']
        )
```
> Send user query to the email agent.

---

```python
        if result['success']:
            answer = result['response'].get('answer', 'Sorry, I could not process that request.')
            formatted_answer = format_response(answer)
            
            # Add to chat history
            instances['chat_history'].append({'role': 'user', 'content': query})
            instances['chat_history'].append({
                'role': 'assistant', 
                'content': formatted_answer
            })
            
            result['response']['answer'] = formatted_answer
        
        return jsonify(result)
```
> Format response and save to chat history.

---

### POST /api/generate-reply

```python
@app.route('/api/generate-reply', methods=['POST'])
def generate_reply():
    """Generate a reply for an email"""
    instances = get_or_create_instances()
    
    data = request.json
    email_id = data.get('email_id')
    user_instruction = data.get('instruction', '')
    
    if not email_id:
        return jsonify({'success': False, 'error': 'No email ID provided'})
    
    # Find the email
    email = next((e for e in instances['inbox'] if e.get('id') == email_id), None)
    
    if not email:
        return jsonify({'success': False, 'error': 'Email not found'})
    
    try:
        result = instances['email_agent'].generate_reply(email, user_instruction)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```
> Generate AI reply for a specific email.

---

### POST /api/save-draft

```python
@app.route('/api/save-draft', methods=['POST'])
def save_draft():
    """Save an email draft"""
    instances = get_or_create_instances()
    
    data = request.json
    draft = {
        'id': f"draft_{len(instances.get('drafts', []))}_{int(time.time())}",
        'to': data.get('to', ''),
        'subject': data.get('subject', ''),
        'body': data.get('body', ''),
        'timestamp': datetime.now().isoformat(),
        'in_reply_to': data.get('in_reply_to'),
        'folder': 'drafts'
    }
    
    if 'drafts' not in instances:
        instances['drafts'] = []
    
    instances['drafts'].append(draft)
    
    return jsonify({'success': True, 'draft': draft})
```
> Save a new draft to session storage.

---

### POST /api/update-prompt

```python
@app.route('/api/update-prompt', methods=['POST'])
def update_prompt():
    """Update a prompt"""
    instances = get_or_create_instances()
    
    data = request.json
    prompt_type = data.get('type')
    new_prompt = data.get('prompt')
    
    try:
        prompt_manager = instances['prompt_manager']
        all_prompts = prompt_manager.get_all_prompts()
        
        if prompt_type in all_prompts:
            prompt_data = all_prompts[prompt_type]
            prompt_data['prompt'] = new_prompt
            prompt_manager.update_prompt(prompt_type, prompt_data)
            
            # Handle read-only filesystem (Vercel)
            if getattr(prompt_manager, 'read_only', False):
                return jsonify({'success': True, 'message': 'Saved in memory only'})
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Prompt type not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```
> Update a prompt template.

---

### POST /api/test-prompt

```python
@app.route('/api/test-prompt', methods=['POST'])
def test_prompt():
    """Test a prompt with an email"""
    instances = get_or_create_instances()
    
    data = request.json
    prompt_template = data.get('prompt')
    email_id = data.get('email_id')
    
    # Find email
    email = next((e for e in instances['inbox'] if e['id'] == email_id), None)
    if not email:
        return jsonify({'success': False, 'error': 'Email not found'})
    
    try:
        # Safe placeholder replacement
        formatted_prompt = (prompt_template
            .replace('{sender}', email.get('sender', ''))
            .replace('{subject}', email.get('subject', ''))
            .replace('{body}', email.get('body', ''))
        )

        # Call LLM
        result = instances['llm_client'].call_llm(formatted_prompt)
        
        return jsonify({
            'success': True,
            'formatted_prompt': formatted_prompt,
            'response': result.get('response'),
            'raw_response': result.get('raw_response')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
```
> Test a prompt template with a real email.

---

## 7. Helper Functions

### format_response()

```python
def format_response(text: str) -> str:
    """Format and clean LLM response for display"""
    if not text:
        return text
    
    import re
    from html import unescape
    
    # Remove any HTML tags completely
    text = re.sub(r'<[^>]+>', '', text)
    
    # Unescape any HTML entities
    text = unescape(text)
    
    # Remove markdown bold/italic
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
    
    # Remove markdown headers
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    
    # Convert numbered lists to cleaner format
    text = re.sub(r'^\d+\.\s+', '• ', text, flags=re.MULTILINE)
    
    # Convert markdown lists to bullet points
    text = re.sub(r'^\*\s+', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'^-\s+', '• ', text, flags=re.MULTILINE)
    
    return text.strip()
```
> Clean AI responses for display:
> - Remove HTML tags
> - Remove markdown formatting
> - Convert lists to bullet points

---

## 8. Application Entry Point

```python
# For Vercel serverless deployment
application = app
```
> Vercel looks for `application` variable for WSGI apps.
> This creates an alias.

---

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```
> Start the Flask development server when run directly.
> - `debug=True` = auto-reload on code changes
> - `host='0.0.0.0'` = accept connections from any IP
> - `port=5000` = listen on port 5000

---

## 📊 Route Summary

### Page Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Redirect to inbox |
| `/inbox` | GET | Show inbox with filters |
| `/starred` | GET | Show starred emails |
| `/snoozed` | GET | Show snoozed emails |
| `/sent` | GET | Show sent emails |
| `/drafts` | GET | Show drafts |
| `/chat` | GET | Show chat interface |
| `/prompt-brain` | GET | Show prompt editor |
| `/setup` | GET/POST | API key setup |

### API Routes

| Route | Method | Purpose |
|-------|--------|---------|
| `/api/load-inbox` | POST | Load mock inbox |
| `/api/process-all` | POST | Process all emails |
| `/api/process-email/<id>` | POST | Process single email |
| `/api/categorize-all` | POST | Categorize all emails |
| `/api/select-email/<id>` | POST | Select an email |
| `/api/deselect-email` | POST | Deselect email |
| `/api/chat` | POST | Send chat query |
| `/api/clear-chat` | POST | Clear chat history |
| `/api/generate-reply` | POST | Generate email reply |
| `/api/save-draft` | POST | Save a draft |
| `/api/delete-draft/<id>` | DELETE | Delete a draft |
| `/api/export-draft/<id>` | GET | Export draft as text |
| `/api/update-prompt` | POST | Update prompt template |
| `/api/test-prompt` | POST | Test a prompt |
| `/api/generate-new-draft` | POST | Generate new draft |

---

## 🔄 Request Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Request                              │
│                             │                                    │
│                             ▼                                    │
│                    ┌─────────────────┐                          │
│                    │   Flask Route   │                          │
│                    │   Handler       │                          │
│                    └────────┬────────┘                          │
│                             │                                    │
│                             ▼                                    │
│                    ┌─────────────────┐                          │
│                    │ get_or_create_  │                          │
│                    │   instances()   │                          │
│                    └────────┬────────┘                          │
│                             │                                    │
│              ┌──────────────┼──────────────┐                    │
│              │              │              │                    │
│              ▼              ▼              ▼                    │
│       ┌──────────┐   ┌──────────┐   ┌──────────┐               │
│       │LLMClient │   │PromptMgr │   │EmailAgent│               │
│       └──────────┘   └──────────┘   └──────────┘               │
│              │              │              │                    │
│              └──────────────┼──────────────┘                    │
│                             │                                    │
│                             ▼                                    │
│                    ┌─────────────────┐                          │
│                    │   Response      │                          │
│                    │ (JSON or HTML)  │                          │
│                    └─────────────────┘                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💡 Key Design Patterns

### 1. Session-Based Instances
Each user gets their own set of components stored in `app_instances`.

### 2. Dependency Injection
Components are created with their dependencies passed in:
```python
instances['email_processor'] = EmailProcessor(
    instances['llm_client'],      # Dependency 1
    instances['prompt_manager']   # Dependency 2
)
```

### 3. REST API Pattern
- `GET` = retrieve data (pages)
- `POST` = create/update data
- `DELETE` = remove data

### 4. Error Handling
All API endpoints wrap in try/except and return consistent JSON:
```python
{'success': True, ...}   # On success
{'success': False, 'error': '...'}  # On failure
```

---

*Last Updated: December 18, 2025*
