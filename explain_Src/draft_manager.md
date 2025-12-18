# 📝 Draft Manager - Explained Line by Line

> **File:** `src/draft_manager.py`  
> **Purpose:** Manages email draft generation and storage (never sends emails)  
> **Lines:** 217

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [Imports](#2-imports)
3. [Class Definition](#3-class-definition)
4. [Constructor (__init__)](#4-constructor-__init__)
5. [load_drafts()](#5-load_drafts)
6. [save_drafts()](#6-save_drafts)
7. [generate_reply_draft()](#7-generate_reply_draft)
8. [generate_new_email_draft()](#8-generate_new_email_draft)
9. [get_draft()](#9-get_draft)
10. [get_all_drafts()](#10-get_all_drafts)
11. [update_draft()](#11-update_draft)
12. [delete_draft()](#12-delete_draft)
13. [export_draft_as_text()](#13-export_draft_as_text)

---

## 1. Overview

The `DraftManager` class is responsible for:
- ✅ Generating reply drafts for existing emails using AI
- ✅ Creating new email drafts from scratch
- ✅ Saving drafts to a JSON file
- ✅ Loading drafts from storage
- ✅ Editing and deleting drafts
- ✅ Exporting drafts as plain text

**🔒 Safety Feature:** This class ONLY creates drafts - it never actually sends emails!

---

## 2. Imports

```python
"""
Draft Manager for Email Productivity Agent
Handles draft generation and storage (never sends emails)
"""
```
> This is a docstring that describes what this file does. It's like a comment at the top of the file.

---

```python
import json
```
> `json` module helps us read and write JSON files. We use it to save drafts to `drafts.json`.

---

```python
import os
```
> `os` module lets us work with files and folders - like checking if a file exists or creating directories.

---

```python
from typing import Dict, Any, List, Optional
```
> These are **type hints** - they tell other developers what type of data our functions expect:
> - `Dict` = dictionary (like `{"key": "value"}`)
> - `Any` = any type of data
> - `List` = a list (like `[1, 2, 3]`)
> - `Optional` = the value can be the specified type OR `None`

---

```python
from datetime import datetime
```
> `datetime` helps us work with dates and times. We use it to timestamp when drafts are created.

---

```python
from src.llm_client import LLMClient
```
> Import the `LLMClient` class from our project. This is what talks to the Gemini AI.

---

```python
from src.prompt_manager import PromptManager
```
> Import the `PromptManager` class. This handles our AI prompt templates.

---

## 3. Class Definition

```python
class DraftManager:
    """Manages email draft generation and storage"""
```
> This creates a new class called `DraftManager`. A class is like a blueprint for creating objects.
> The docstring describes what this class does.

---

## 4. Constructor (__init__)

```python
def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager):
```
> The **constructor** - this runs when you create a new `DraftManager` object.
> - `self` = refers to the object itself
> - `llm_client` = the AI client we'll use to generate drafts
> - `prompt_manager` = manages our prompt templates

---

```python
    self.llm_client = llm_client
```
> Store the AI client so we can use it later in other methods.

---

```python
    self.prompt_manager = prompt_manager
```
> Store the prompt manager for later use.

---

```python
    self.drafts = {}
```
> Create an empty dictionary to hold all our drafts. Format: `{"draft_id": draft_data}`

---

```python
    self.drafts_file = "data/drafts.json"
```
> The file path where we'll save our drafts. All drafts persist to this JSON file.

---

```python
    self.load_drafts()
```
> Immediately load any existing drafts from the file when the DraftManager is created.

---

## 5. load_drafts()

```python
def load_drafts(self):
    """Load saved drafts from file"""
```
> Method to load drafts from the JSON file into memory.

---

```python
    if os.path.exists(self.drafts_file):
```
> Check if the drafts file exists before trying to read it. Prevents errors if file doesn't exist.

---

```python
        with open(self.drafts_file, 'r', encoding='utf-8') as f:
```
> Open the file for reading (`'r'`). The `with` statement automatically closes the file when done.
> `encoding='utf-8'` ensures we can read special characters correctly.

---

```python
            self.drafts = json.load(f)
```
> Read the JSON file and convert it to a Python dictionary. Store it in `self.drafts`.

---

## 6. save_drafts()

```python
def save_drafts(self):
    """Save drafts to file"""
```
> Method to save all drafts from memory to the JSON file.

---

```python
    os.makedirs(os.path.dirname(self.drafts_file), exist_ok=True)
```
> Create the directory if it doesn't exist.
> - `os.path.dirname()` gets the folder path (`"data/"`)
> - `exist_ok=True` means don't error if folder already exists

---

```python
    with open(self.drafts_file, 'w', encoding='utf-8') as f:
```
> Open the file for writing (`'w'`). This will overwrite the existing file.

---

```python
        json.dump(self.drafts, f, indent=2, ensure_ascii=False)
```
> Write the drafts dictionary to the file as JSON.
> - `indent=2` makes it pretty-printed (easier to read)
> - `ensure_ascii=False` allows non-English characters

---

## 7. generate_reply_draft()

```python
def generate_reply_draft(
    self, 
    original_email: Dict[str, Any],
    custom_instructions: Optional[str] = None
) -> Dict[str, Any]:
```
> Generate a reply to an existing email.
> - `original_email` = the email we're replying to
> - `custom_instructions` = optional extra instructions (e.g., "be more formal")
> - Returns a dictionary with the draft data

---

```python
    """
    Generate a reply draft for an email
    
    Args:
        original_email: The email to reply to
        custom_instructions: Optional custom instructions for the reply
        
    Returns:
        Draft data with subject, body, metadata
    """
```
> Docstring explaining what the function does, its parameters, and return value.

---

```python
    prompt = self.prompt_manager.format_prompt("auto_reply", original_email)
```
> Get the "auto_reply" prompt template and fill in the email details.
> The prompt manager replaces `{sender}`, `{subject}`, `{body}` with actual values.

---

```python
    if custom_instructions:
        prompt += f"\n\nAdditional Instructions: {custom_instructions}"
```
> If the user provided custom instructions, add them to the prompt.
> This lets users say things like "be more casual" or "include a meeting request".

---

```python
    result = self.llm_client.call_llm(prompt, temperature=0.7)
```
> Send the prompt to the AI and get a response.
> `temperature=0.7` makes the AI somewhat creative (0=robotic, 1=very creative).

---

```python
    if not result["success"]:
        return {
            "success": False,
            "error": result["error"],
            "draft": None
        }
```
> If the AI call failed, return an error response. Don't create a draft.

---

```python
    draft = {
        "id": f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
```
> Create a unique ID for the draft using the current date and time.
> Example: `"draft_20251218_143022"`

---

```python
        "created_at": datetime.now().isoformat(),
```
> Store when the draft was created in ISO format.
> Example: `"2025-12-18T14:30:22.123456"`

---

```python
        "original_email_id": original_email.get("id"),
```
> Store the ID of the email we're replying to.

---

```python
        "in_reply_to": {
            "sender": original_email.get("sender"),
            "subject": original_email.get("subject")
        },
```
> Store info about the original email for reference.

---

```python
        "draft_content": result["response"],
```
> The actual reply content generated by the AI (subject, body, tone, etc.).

---

```python
        "prompt_used": result["prompt_used"],
```
> Store the prompt we used - helpful for debugging.

---

```python
        "status": "draft",  # Always draft, never sent
```
> Mark as "draft". This is a safety feature - we never auto-send!

---

```python
        "custom_instructions": custom_instructions
```
> Store any custom instructions the user provided.

---

```python
    }
    
    self.drafts[draft["id"]] = draft
```
> Add the new draft to our drafts dictionary.

---

```python
    self.save_drafts()
```
> Save all drafts to the JSON file immediately.

---

```python
    return {
        "success": True,
        "draft": draft,
        "error": None
    }
```
> Return a success response with the created draft.

---

## 8. generate_new_email_draft()

```python
def generate_new_email_draft(
    self,
    recipient: str,
    subject: str,
    context: str,
    tone: str = "professional"
) -> Dict[str, Any]:
```
> Generate a brand new email (not a reply).
> - `recipient` = who to send to
> - `subject` = email subject line
> - `context` = what the email should be about
> - `tone` = style of writing (default: professional)

---

```python
    """
    Generate a new email draft from scratch
    
    Args:
        recipient: Email recipient
        subject: Email subject
        context: Context/instructions for the email
        tone: Desired tone (professional, friendly, formal)
        
    Returns:
        Draft data
    """
```
> Documentation for the function.

---

```python
    prompt = f"""Generate a new email with the following details:

Recipient: {recipient}
Subject: {subject}
Context: {context}
Tone: {tone}

Create a complete, professional email that addresses the context appropriately.

Respond in JSON format:
{{
  "subject": "<email subject>",
  "body": "<email body>",
  "tone": "<actual tone used>",
  "suggested_actions": ["<follow-up 1>", "<follow-up 2>"]
}}"""
```
> Build a custom prompt for creating a new email.
> We tell the AI exactly what format we want the response in (JSON).
> Note: `{{` and `}}` are escaped braces (they show as `{` and `}` in the output).

---

```python
    result = self.llm_client.call_llm(prompt, temperature=0.7)
```
> Call the AI with our prompt.

---

```python
    if not result["success"]:
        return {
            "success": False,
            "error": result["error"],
            "draft": None
        }
```
> Handle AI errors.

---

```python
    draft = {
        "id": f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created_at": datetime.now().isoformat(),
        "type": "new",
```
> Create the draft object. `"type": "new"` indicates this is a new email, not a reply.

---

```python
        "recipient": recipient,
```
> Store who the email is for.

---

```python
        "draft_content": result["response"],
        "prompt_used": result["prompt_used"],
        "status": "draft",
        "context": context
    }
```
> Store the AI response and other metadata.

---

```python
    self.drafts[draft["id"]] = draft
    self.save_drafts()
```
> Save the draft to memory and file.

---

```python
    return {
        "success": True,
        "draft": draft,
        "error": None
    }
```
> Return success response.

---

## 9. get_draft()

```python
def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
    """Get a specific draft by ID"""
    return self.drafts.get(draft_id)
```
> Get a single draft by its ID.
> - `self.drafts.get(draft_id)` returns the draft if found, or `None` if not found.
> - This is safer than `self.drafts[draft_id]` which would crash if ID doesn't exist.

---

## 10. get_all_drafts()

```python
def get_all_drafts(self) -> List[Dict[str, Any]]:
    """Get all drafts"""
    return list(self.drafts.values())
```
> Get all drafts as a list.
> - `self.drafts.values()` gets all the draft objects (ignoring the IDs)
> - `list()` converts it from a dict_values object to a regular list

---

## 11. update_draft()

```python
def update_draft(self, draft_id: str, updates: Dict[str, Any]):
    """Update a draft"""
```
> Update an existing draft with new data.

---

```python
    if draft_id in self.drafts:
```
> Only proceed if the draft exists.

---

```python
        self.drafts[draft_id].update(updates)
```
> Merge the new data into the existing draft.
> `.update()` adds/overwrites keys from `updates` into the draft.

---

```python
        self.drafts[draft_id]["updated_at"] = datetime.now().isoformat()
```
> Record when the draft was last updated.

---

```python
        self.save_drafts()
```
> Save changes to file.

---

## 12. delete_draft()

```python
def delete_draft(self, draft_id: str):
    """Delete a draft"""
```
> Remove a draft permanently.

---

```python
    if draft_id in self.drafts:
        del self.drafts[draft_id]
```
> If the draft exists, delete it from the dictionary.

---

```python
        self.save_drafts()
```
> Save the updated drafts (without the deleted one) to file.

---

## 13. export_draft_as_text()

```python
def export_draft_as_text(self, draft_id: str) -> str:
    """Export draft as formatted text"""
```
> Convert a draft to a nicely formatted plain text string.
> Useful for downloading or copying.

---

```python
    draft = self.drafts.get(draft_id)
    if not draft:
        return ""
```
> Get the draft. Return empty string if not found.

---

```python
    content = draft.get("draft_content", {})
```
> Get the AI-generated content (subject, body, etc.).

---

```python
    export_text = f"""Draft Email
{'='*50}
Created: {draft.get('created_at')}
Status: {draft.get('status')}

"""
```
> Start building the export text with a header.
> `{'='*50}` creates a line of 50 equal signs: `==================================================`

---

```python
    if "in_reply_to" in draft:
        export_text += f"""In Reply To:
  From: {draft['in_reply_to'].get('sender')}
  Subject: {draft['in_reply_to'].get('subject')}

"""
```
> If this is a reply, include info about the original email.

---

```python
    export_text += f"""Subject: {content.get('subject', 'No Subject')}

Body:
{content.get('body', '')}

"""
```
> Add the subject and body. Use defaults if not found.

---

```python
    if content.get('suggested_actions'):
        export_text += f"""Suggested Follow-ups:
"""
        for action in content.get('suggested_actions', []):
            export_text += f"  - {action}\n"
```
> If there are suggested follow-up actions, list them with bullet points.

---

```python
    return export_text
```
> Return the complete formatted text.

---

## 📊 Visual Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                      DraftManager                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────┐   │
│  │  LLMClient   │    │PromptManager │    │  drafts.json     │   │
│  │  (AI calls)  │    │ (templates)  │    │  (storage)       │   │
│  └──────┬───────┘    └──────┬───────┘    └────────┬─────────┘   │
│         │                   │                     │              │
│         └───────────────────┼─────────────────────┘              │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Methods                                │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  📥 load_drafts()      - Load from JSON file             │   │
│  │  💾 save_drafts()      - Save to JSON file               │   │
│  │  ↩️  generate_reply_draft() - AI reply to email          │   │
│  │  ✉️  generate_new_email_draft() - AI new email           │   │
│  │  🔍 get_draft()        - Get one draft by ID             │   │
│  │  📋 get_all_drafts()   - Get all drafts as list          │   │
│  │  ✏️  update_draft()     - Edit existing draft             │   │
│  │  🗑️  delete_draft()     - Remove a draft                  │   │
│  │  📤 export_draft_as_text() - Convert to plain text       │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow

### Creating a Reply Draft:
```
User clicks "Reply"
        │
        ▼
┌─────────────────────┐
│ generate_reply_draft│
│ (original_email)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ prompt_manager      │
│ .format_prompt()    │──▶ "Reply to email from John about Project..."
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ llm_client          │
│ .call_llm()         │──▶ Gemini AI
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Create draft object │
│ with ID, timestamp  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ save_drafts()       │──▶ data/drafts.json
└──────────┬──────────┘
           │
           ▼
    Return success + draft
```

---

## 📦 Draft Object Structure

```json
{
  "id": "draft_20251218_143022",
  "created_at": "2025-12-18T14:30:22.123456",
  "original_email_id": "e001",
  "in_reply_to": {
    "sender": "john@example.com",
    "subject": "Project Update"
  },
  "draft_content": {
    "subject": "Re: Project Update",
    "body": "Hi John, thank you for the update...",
    "tone": "professional",
    "suggested_actions": ["Schedule follow-up call"]
  },
  "prompt_used": "Generate a reply for...",
  "status": "draft",
  "custom_instructions": null
}
```

---

*Last Updated: December 18, 2025*
