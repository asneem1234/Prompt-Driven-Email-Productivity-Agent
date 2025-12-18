# 📝 Prompt Manager - Explained Line by Line

> **File:** `src/prompt_manager.py`  
> **Purpose:** Manages prompt templates with loading, saving, formatting, and versioning  
> **Lines:** 130

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [Imports](#2-imports)
3. [Class Definition](#3-class-definition)
4. [Constructor (__init__)](#4-constructor-__init__)
5. [load_prompts()](#5-load_prompts)
6. [save_prompts()](#6-save_prompts)
7. [get_prompt()](#7-get_prompt)
8. [update_prompt()](#8-update_prompt)
9. [format_prompt()](#9-format_prompt)
10. [get_all_prompts()](#10-get_all_prompts)
11. [get_prompt_history()](#11-get_prompt_history)
12. [_get_default_prompts()](#12-_get_default_prompts)

---

## 1. Overview

The `PromptManager` class is the **prompt template system** that:
- 📂 **Loads** prompts from a JSON file
- 💾 **Saves** prompts back to the file
- 🔄 **Formats** prompts with email data (replaces placeholders)
- 📜 **Tracks** version history of prompt changes
- 🌐 **Handles** read-only environments (like Vercel serverless)

**Key Design:** All AI behavior is controlled through editable prompts. Users can customize how the AI categorizes, summarizes, and replies to emails through the "Prompt Brain" UI.

---

## 2. Imports

```python
"""
Prompt Manager for Email Productivity Agent
Handles loading, saving, and formatting prompts
"""
```
> Docstring describing the file's purpose.

---

```python
import json
```
> `json` module for reading and writing JSON files.
> Prompts are stored in `data/default_prompts.json`.

---

```python
import os
```
> `os` module for file operations:
> - Check if file exists (`os.path.exists`)
> - Create directories (`os.makedirs`)
> - Get directory name (`os.path.dirname`)

---

```python
from typing import Dict, Any, Optional
```
> Type hints for better code documentation:
> - `Dict` = dictionary like `{"key": "value"}`
> - `Any` = any data type
> - `Optional` = can be the type OR `None`

---

```python
from datetime import datetime
```
> `datetime` for timestamping prompt changes in the history.

---

## 3. Class Definition

```python
class PromptManager:
    """Manages prompt templates with versioning and formatting"""
```
> Create the `PromptManager` class.
> This is the central hub for all prompt operations.

---

## 4. Constructor (__init__)

```python
def __init__(self, prompts_file: str = "data/default_prompts.json"):
```
> Constructor - runs when creating a new PromptManager.
> - `prompts_file` = path to the JSON file storing prompts
> - Default: `"data/default_prompts.json"`

---

```python
    self.prompts_file = prompts_file
```
> Store the file path for later use when loading/saving.

---

```python
    self.prompts = {}
```
> Empty dictionary to hold all prompts.
> Format: `{"prompt_type": prompt_data, ...}`

---

```python
    self.prompt_history = []
```
> Empty list to track all changes (version history).
> Each entry has timestamp and the prompts at that time.

---

```python
    # If the deployment environment is read-only (e.g. Vercel), we'll
    # keep an in-memory copy of prompts and avoid failing when saving.
    self.read_only = False
```
> Flag to track if we're in a read-only environment.
> Serverless platforms like Vercel don't allow file writes.

---

```python
    self._in_memory_prompts = {}
```
> Backup storage for when we can't write to disk.
> The underscore `_` indicates this is a "private" variable.

---

```python
    self.load_prompts()
```
> Immediately load prompts when the PromptManager is created.

---

## 5. load_prompts()

```python
def load_prompts(self):
    """Load prompts from JSON file"""
```
> Load prompts from the JSON file into memory.

---

```python
    try:
        if os.path.exists(self.prompts_file):
```
> Check if the prompts file exists before trying to read it.

---

```python
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                self.prompts = json.load(f)
```
> Open the file and parse the JSON into a Python dictionary.
> `encoding='utf-8'` ensures special characters work correctly.

---

```python
        else:
            # Create default prompts if file doesn't exist
            self.prompts = self._get_default_prompts()
```
> If file doesn't exist, use the built-in default prompts.

---

```python
            try:
                self.save_prompts()
            except OSError:
                # If we cannot write to disk, fallback to in-memory prompts
                self.read_only = True
                self._in_memory_prompts = self.prompts.copy()
```
> Try to save the defaults to create the file.
> If that fails (read-only environment), switch to in-memory mode.

---

```python
    except (OSError, PermissionError) as e:
        # Running in a read-only environment (e.g., serverless deployment)
        # Use an in-memory fallback so the UI still works but changes are ephemeral.
        self.read_only = True
        if not self._in_memory_prompts:
            self._in_memory_prompts = self._get_default_prompts()
        self.prompts = self._in_memory_prompts.copy()
```
> If loading fails (permissions, etc.), fall back to in-memory defaults.
> The UI will still work, but changes won't persist after restart.

---

## 6. save_prompts()

```python
def save_prompts(self):
    """Save prompts to JSON file"""
```
> Save current prompts to the JSON file.

---

```python
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.prompts_file), exist_ok=True)
```
> Create the directory if it doesn't exist.
> `exist_ok=True` means don't error if it already exists.

---

```python
        with open(self.prompts_file, 'w', encoding='utf-8') as f:
            json.dump(self.prompts, f, indent=2, ensure_ascii=False)
```
> Write prompts to file as formatted JSON.
> - `indent=2` makes it human-readable
> - `ensure_ascii=False` allows non-English characters

---

```python
        # Add to history
        self.prompt_history.append({
            "timestamp": datetime.now().isoformat(),
            "prompts": self.prompts.copy()
        })
```
> Record this version in the history with a timestamp.
> `.copy()` creates a snapshot (not a reference).

---

```python
        # If we previously thought filesystem was read-only, reset that flag
        self.read_only = False
```
> If save succeeds, we're not in read-only mode.

---

```python
    except (OSError, PermissionError) as e:
        # Filesystem is not writable (common on serverless platforms)
        # Fallback to in-memory storage so users can still edit prompts in the UI.
        self.read_only = True
        self._in_memory_prompts = self.prompts.copy()
```
> If save fails, switch to in-memory mode.
> Prompts still work for this session.

---

```python
        # Record history even for in-memory saves
        self.prompt_history.append({
            "timestamp": datetime.now().isoformat(),
            "prompts": self.prompts.copy(),
            "note": "saved-in-memory"
        })
```
> Still record history, but note it's in-memory only.

---

## 7. get_prompt()

```python
def get_prompt(self, prompt_type: str) -> Optional[Dict[str, Any]]:
    """Get a specific prompt by type"""
    return self.prompts.get(prompt_type)
```
> Get a single prompt by its type name.
> - `prompt_type` = "categorization", "action_extraction", "auto_reply", etc.
> - Returns the prompt data or `None` if not found

---

## 8. update_prompt()

```python
def update_prompt(self, prompt_type: str, prompt_data: Dict[str, Any]):
    """Update a prompt template"""
    self.prompts[prompt_type] = prompt_data
```
> Update (or create) a prompt with new data.
> This is called when users edit prompts in the "Prompt Brain" UI.

---

```python
    # Attempt to persist; if running in read-only environment this will
    # fallback to an in-memory store and set `self.read_only`.
    try:
        self.save_prompts()
    except Exception:
        # Save failure already handled inside save_prompts; just ensure
        # prompts are available in-memory for the session.
        self._in_memory_prompts = self.prompts.copy()
```
> Try to save to disk, but if it fails, keep the changes in memory.
> Users can still use their edited prompts during this session.

---

## 9. format_prompt()

This is the **key method** that fills in email data into prompt templates.

```python
def format_prompt(self, prompt_type: str, email_data: Dict[str, Any]) -> str:
    """
    Format a prompt template with email data
    
    Args:
        prompt_type: Type of prompt (categorization, action_extraction, etc.)
        email_data: Email data dict with sender, subject, body
        
    Returns:
        Formatted prompt string
    """
```
> Take a prompt template and fill in the actual email values.

---

```python
    prompt_template = self.prompts.get(prompt_type)
    if not prompt_template:
        raise ValueError(f"Prompt type '{prompt_type}' not found")
```
> Get the prompt template. Error if it doesn't exist.

---

```python
    template = prompt_template.get("prompt", "")
```
> Get the actual prompt text from the template object.

---

```python
    # Replace placeholders manually to avoid issues with JSON braces in template
    formatted_prompt = template.replace("{sender}", email_data.get("sender", "Unknown"))
    formatted_prompt = formatted_prompt.replace("{subject}", email_data.get("subject", "No Subject"))
    formatted_prompt = formatted_prompt.replace("{body}", email_data.get("body", ""))
```
> **String replacement:** Replace placeholders with actual email values.
> - `{sender}` → actual sender email
> - `{subject}` → actual subject line
> - `{body}` → actual email body
>
> **Why not `.format()`?** Because prompts contain JSON with `{` and `}` braces,
> which would confuse Python's string formatting.

---

```python
    return formatted_prompt
```
> Return the complete prompt ready to send to the AI.

---

## 10. get_all_prompts()

```python
def get_all_prompts(self) -> Dict[str, Any]:
    """Get all prompts"""
    return self.prompts
```
> Return all prompts as a dictionary.
> Used by the "Prompt Brain" UI to display all editable prompts.

---

## 11. get_prompt_history()

```python
def get_prompt_history(self) -> list:
    """Get prompt version history"""
    return self.prompt_history
```
> Return the list of all prompt versions.
> Could be used for undo/versioning features.

---

## 12. _get_default_prompts()

```python
def _get_default_prompts(self) -> Dict[str, Any]:
    """Return default prompt templates"""
```
> Return the built-in default prompts.
> Used when no JSON file exists.
> The underscore `_` indicates this is a "private" method.

---

```python
    return {
        "categorization": {
            "name": "Email Categorization",
            "prompt": "Categorize this email: From: {sender}, Subject: {subject}, Body: {body}",
            "description": "Categorizes emails"
        },
```
> **Categorization prompt:** Simple default for classifying emails.
> The real prompt in `default_prompts.json` is much more detailed.

---

```python
        "action_extraction": {
            "name": "Action Item Extraction",
            "prompt": "Extract action items from: {body}",
            "description": "Extracts tasks"
        },
```
> **Action extraction prompt:** For finding tasks/deadlines.

---

```python
        "auto_reply": {
            "name": "Auto-Reply Generator",
            "prompt": "Generate reply for: {body}",
            "description": "Generates replies"
        }
    }
```
> **Auto-reply prompt:** For generating email responses.

---

## 📊 Visual Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                      PromptManager                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Properties                             │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  📄 prompts_file     - Path to JSON file                 │   │
│  │  📦 prompts          - All loaded prompts                │   │
│  │  📜 prompt_history   - Version history                   │   │
│  │  🔒 read_only        - Read-only environment flag        │   │
│  │  💾 _in_memory_prompts - Backup for serverless           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      Methods                              │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  📥 load_prompts()      - Load from JSON file            │   │
│  │  💾 save_prompts()      - Save to JSON file              │   │
│  │  🔍 get_prompt()        - Get one prompt by type         │   │
│  │  ✏️  update_prompt()     - Update/create a prompt         │   │
│  │  🔄 format_prompt()     - Fill in email placeholders     │   │
│  │  📋 get_all_prompts()   - Get all prompts                │   │
│  │  📜 get_prompt_history()- Get version history            │   │
│  │  🏠 _get_default_prompts() - Built-in defaults           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Format Prompt Flow

```
     Template                      Email Data
         │                              │
         │  "Categorize this email:     │  {
         │   From: {sender},            │    "sender": "john@example.com",
         │   Subject: {subject},        │    "subject": "Meeting Tomorrow",
         │   Body: {body}"              │    "body": "Hi, can we meet at 3pm?"
         │                              │  }
         │                              │
         └──────────────┬───────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │   format_prompt()   │
              │                     │
              │  1. Get template    │
              │  2. Replace {sender}│
              │  3. Replace {subject}
              │  4. Replace {body}  │
              └──────────┬──────────┘
                         │
                         ▼
              
     "Categorize this email:
      From: john@example.com,
      Subject: Meeting Tomorrow,
      Body: Hi, can we meet at 3pm?"
              
                         │
                         ▼
                   Send to AI
```

---

## 📦 Prompt Template Structure

Each prompt in the JSON file looks like this:

```json
{
  "categorization": {
    "name": "Email Categorization",
    "prompt": "You are an email categorization assistant. Analyze the following email...\n\nFrom: {sender}\nSubject: {subject}\nBody:\n{body}\n\nRespond in JSON format...",
    "description": "Categorizes emails with color-coded categories"
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Display name in UI |
| `prompt` | string | The actual AI prompt with placeholders |
| `description` | string | Short description for users |

---

## 🏷️ Available Prompt Types

| Type | Purpose | Placeholders |
|------|---------|--------------|
| `categorization` | Classify emails | `{sender}`, `{subject}`, `{body}` |
| `action_extraction` | Extract tasks/deadlines | `{sender}`, `{subject}`, `{body}` |
| `auto_reply` | Generate email replies | `{sender}`, `{subject}`, `{body}` |
| `summarization` | Summarize email content | `{sender}`, `{subject}`, `{body}` |

---

## 🌐 Read-Only Environment Handling

```
┌─────────────────────────────────────────────────────────────────┐
│                    Environment Detection                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────┐    ┌─────────────────────────────┐ │
│  │   Local Development     │    │   Serverless (Vercel)       │ │
│  ├─────────────────────────┤    ├─────────────────────────────┤ │
│  │ • File system writable  │    │ • File system read-only     │ │
│  │ • read_only = False     │    │ • read_only = True          │ │
│  │ • Saves to JSON file    │    │ • Saves to memory only      │ │
│  │ • Changes persist       │    │ • Changes are ephemeral     │ │
│  └─────────────────────────┘    └─────────────────────────────┘ │
│                                                                  │
│  Both environments:                                              │
│  ✅ UI works normally                                            │
│  ✅ Users can edit prompts                                       │
│  ✅ Edited prompts work for the session                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📜 Version History Structure

```python
prompt_history = [
    {
        "timestamp": "2025-12-18T10:30:00.000000",
        "prompts": {
            "categorization": {...},
            "action_extraction": {...}
        }
    },
    {
        "timestamp": "2025-12-18T14:45:22.123456",
        "prompts": {
            "categorization": {...},  # Updated!
            "action_extraction": {...}
        },
        "note": "saved-in-memory"  # Only if serverless
    }
]
```

---

## 💡 Usage Examples

### Get and Format a Prompt
```python
# Create manager
pm = PromptManager()

# Get the categorization prompt template
template = pm.get_prompt("categorization")
print(template["name"])  # "Email Categorization"

# Format with email data
email = {
    "sender": "boss@company.com",
    "subject": "Urgent: Review needed",
    "body": "Please review the attached document ASAP."
}
formatted = pm.format_prompt("categorization", email)
print(formatted)  # Ready to send to AI!
```

### Update a Prompt
```python
# Get existing prompt
prompt = pm.get_prompt("auto_reply")

# Modify it
prompt["prompt"] = "Generate a friendly reply to: {body}"

# Save it
pm.update_prompt("auto_reply", prompt)
```

### Check All Prompts
```python
all_prompts = pm.get_all_prompts()
for prompt_type, data in all_prompts.items():
    print(f"{prompt_type}: {data['name']}")
```

### View History
```python
history = pm.get_prompt_history()
for version in history:
    print(f"Saved at: {version['timestamp']}")
```

---

## 🔐 Why Prompts are Important

The prompt-driven architecture means:

| Benefit | Description |
|---------|-------------|
| **Customizable** | Users can change AI behavior without coding |
| **Transparent** | See exactly what instructions the AI receives |
| **Testable** | Try different prompts in the "Prompt Brain" UI |
| **Versionable** | History tracks all changes |
| **Safe Defaults** | Falls back to working defaults if file is missing |

---

## 📂 File Location

```
project/
├── data/
│   └── default_prompts.json   ◀── Prompts stored here
├── src/
│   └── prompt_manager.py      ◀── This file
└── ...
```

---

*Last Updated: December 18, 2025*
