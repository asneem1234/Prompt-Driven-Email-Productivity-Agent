# 📧 Email Processor - Explained Line by Line

> **File:** `src/email_processor.py`  
> **Purpose:** Processes emails through LLM pipeline for categorization, action extraction, and summarization  
> **Lines:** 216

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [Imports](#2-imports)
3. [Class Definition](#3-class-definition)
4. [Constructor (__init__)](#4-constructor-__init__)
5. [process_email()](#5-process_email---main-pipeline)
6. [categorize_email()](#6-categorize_email)
7. [extract_actions()](#7-extract_actions)
8. [summarize_email()](#8-summarize_email)
9. [process_inbox()](#9-process_inbox)
10. [get_processed_email()](#10-get_processed_email)
11. [get_all_processed_emails()](#11-get_all_processed_emails)
12. [get_emails_by_category()](#12-get_emails_by_category)
13. [get_all_action_items()](#13-get_all_action_items)

---

## 1. Overview

The `EmailProcessor` class is the **processing pipeline** that analyzes emails using AI. It:
- 🏷️ **Categorizes** emails (Urgent, Deadline, Conversation, Spam, Other)
- ✅ **Extracts action items** with deadlines and priorities
- 📝 **Summarizes** email content with key points
- 💾 **Stores** processed results in memory

**Key Design:** Uses a separate "fast model" for categorization to handle bulk processing without hitting rate limits.

---

## 2. Imports

```python
"""
Email Processor for Email Productivity Agent
Handles email ingestion, categorization, and action extraction
"""
```
> Docstring describing the file's purpose.

---

```python
import json
```
> `json` module for parsing JSON responses from the AI.

---

```python
import os
```
> `os` module to access environment variables (API key).

---

```python
from typing import Dict, Any, List, Optional
```
> Type hints for better code documentation:
> - `Dict` = dictionary like `{"key": "value"}`
> - `Any` = any data type
> - `List` = list like `[1, 2, 3]`
> - `Optional` = can be the type OR `None`

---

```python
from datetime import datetime
```
> `datetime` for timestamping when emails are processed.

---

```python
from src.llm_client import LLMClient
```
> Import our LLM client wrapper for Gemini API calls.

---

```python
from src.prompt_manager import PromptManager
```
> Import prompt manager for loading and formatting prompts.

---

```python
import google.generativeai as genai
```
> Import Google's Gemini AI library directly.
> This is used for the "fast model" separate from LLMClient.

---

## 3. Class Definition

```python
class EmailProcessor:
    """Processes emails through LLM pipeline for categorization and extraction"""
```
> Create the `EmailProcessor` class. This handles all email analysis.

---

## 4. Constructor (__init__)

```python
def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager):
```
> Constructor - runs when creating a new EmailProcessor.
> - `llm_client` = the AI client for API calls
> - `prompt_manager` = manages prompt templates

---

```python
    self.llm_client = llm_client
```
> Store the LLM client for summarization and action extraction.

---

```python
    self.prompt_manager = prompt_manager
```
> Store the prompt manager for getting prompt templates.

---

```python
    self.processed_emails = {}
```
> Empty dictionary to store processed email results.
> Format: `{"email_id": processed_data}`

---

```python
    # Create a separate fast model for categorization to avoid rate limits
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
```
> Configure the Gemini library with the API key.
> We're setting up a SECOND model instance here.

---

```python
    self.fast_model = genai.GenerativeModel("gemini-2.0-flash")
```
> Create a separate "fast model" for categorization.
> 
> **Why?** When processing many emails, using a dedicated model
> helps avoid rate limits and is optimized for quick categorization.

---

## 5. process_email() - Main Pipeline

This is the **main processing function** that runs all analysis steps.

```python
def process_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single email through the full pipeline
    
    Args:
        email: Email dict with id, sender, subject, body, etc.
        
    Returns:
        Processed email with category, actions, summary
    """
```
> Process one email through the complete analysis pipeline.

---

```python
    email_id = email.get("id")
```
> Get the email's unique ID for storage.

---

```python
    # Initialize processed data
    processed = {
        "email": email,
        "processed_at": datetime.now().isoformat(),
        "category": None,
        "action_items": [],
        "summary": None,
        "processing_errors": []
    }
```
> Create the result object with all fields initialized.
> - `email` = the original email data
> - `processed_at` = timestamp when we processed it
> - `category` = will hold categorization result
> - `action_items` = will hold extracted tasks
> - `summary` = will hold email summary
> - `processing_errors` = any errors that occur

---

```python
    # Step 1: Categorize email
    try:
        category_result = self.categorize_email(email)
        if category_result["success"]:
            processed["category"] = category_result["response"]
    except Exception as e:
        processed["processing_errors"].append(f"Categorization error: {str(e)}")
```
> **Step 1:** Categorize the email (Urgent, Deadline, etc.)
> Wrapped in try/except so one failure doesn't stop the whole pipeline.

---

```python
    # Step 2: Extract action items
    try:
        actions_result = self.extract_actions(email)
        if actions_result["success"]:
            processed["action_items"] = actions_result["response"].get("action_items", [])
    except Exception as e:
        processed["processing_errors"].append(f"Action extraction error: {str(e)}")
```
> **Step 2:** Extract any tasks/action items from the email.
> Gets the `action_items` list from the response.

---

```python
    # Step 3: Generate summary
    try:
        summary_result = self.summarize_email(email)
        if summary_result["success"]:
            processed["summary"] = summary_result["response"]
    except Exception as e:
        processed["processing_errors"].append(f"Summarization error: {str(e)}")
```
> **Step 3:** Generate a summary of the email.

---

```python
    # Store processed email
    self.processed_emails[email_id] = processed
```
> Save the processed result to our dictionary for later retrieval.

---

```python
    return processed
```
> Return the complete processed email data.

---

## 6. categorize_email()

This method categorizes emails using the fast model with robust error handling.

```python
def categorize_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
    """Categorize email using fast model to avoid rate limits"""
```
> Categorize a single email into one of 5 categories.

---

```python
    import re
    import time
```
> Import `re` for regex (finding retry delays) and `time` for sleeping.
> These are imported inside the function to keep them scoped.

---

```python
    prompt = self.prompt_manager.format_prompt("categorization", email)
```
> Get the categorization prompt and fill in the email details.
> The prompt tells the AI about the 5 categories and how to choose.

---

```python
    # Use Gemini 2.5 Flash for categorization with retry logic
    max_retries = 2
```
> Allow up to 2 retry attempts if something fails.

---

```python
    for attempt in range(max_retries):
```
> Loop through retry attempts (0, 1).

---

```python
        try:
            print(f"      🤖 Calling Gemini API for email {email['id']}...")
```
> Log that we're making an API call (helpful for debugging).

---

```python
            response = self.fast_model.generate_content(
                prompt + "\n\nIMPORTANT: Respond with ONLY valid JSON.",
                generation_config={"temperature": 0.3, "max_output_tokens": 500}
            )
```
> Call the fast Gemini model.
> - `temperature=0.3` = low creativity, consistent categorization
> - `max_output_tokens=500` = keep response short
> - Add instruction for JSON-only response

---

```python
            print(f"      ✓ API response received")
```
> Log success.

---

```python
            # Check for safety blocks
            if not response.candidates or not response.candidates[0].content.parts:
                return {
                    "success": False,
                    "response": {"category": "Other", "confidence": 0.5, "reasoning": "Content filtered"},
                    "error": "Content filtered by safety",
                    "model": "gemini-2.0-flash"
                }
```
> If Google's safety filters blocked the response, return a default "Other" category.

---

```python
            # Parse response - clean up common formatting issues
            raw_response = response.text.strip()
```
> Get the text response and remove whitespace.

---

```python
            # Remove markdown code blocks
            if raw_response.startswith("```json"):
                raw_response = raw_response.split("```json")[1].split("```")[0].strip()
            elif raw_response.startswith("```"):
                raw_response = raw_response.split("```")[1].split("```")[0].strip()
```
> AI sometimes wraps JSON in markdown code blocks. Remove them.
> Example: ` ```json {"category": "Urgent"} ``` ` → `{"category": "Urgent"}`

---

```python
            # Remove any leading/trailing whitespace and newlines
            raw_response = raw_response.strip()
```
> Clean up any remaining whitespace.

---

```python
            # Try to find JSON object if there's extra text
            if not raw_response.startswith("{"):
                # Look for the first { and last }
                start_idx = raw_response.find("{")
                end_idx = raw_response.rfind("}")
                if start_idx != -1 and end_idx != -1:
                    raw_response = raw_response[start_idx:end_idx+1]
```
> If there's text before/after the JSON, extract just the JSON part.
> Example: `Here's the result: {"category": "Urgent"}` → `{"category": "Urgent"}`

---

```python
            parsed_response = json.loads(raw_response)
```
> Parse the JSON string into a Python dictionary.

---

```python
            print(f"      ✓ Parsed category: {parsed_response.get('category', 'Unknown')}")
```
> Log the parsed category for debugging.

---

```python
            return {
                "success": True,
                "response": parsed_response,
                "raw_response": raw_response,
                "model": "gemini-2.0-flash"
            }
```
> Return successful result with the parsed category data.

---

```python
        except Exception as e:
            error_str = str(e)
```
> Catch any errors and convert to string for analysis.

---

```python
            # Check for rate limit with retry delay
            if "429" in error_str or "Quota exceeded" in error_str:
```
> Check if the error is a rate limit (HTTP 429).

---

```python
                # Try to extract retry delay from error message
                retry_match = re.search(r'retry in (\d+(?:\.\d+)?)s', error_str, re.IGNORECASE)
```
> Use regex to find "retry in X.Xs" in the error message.
> Google often tells you how long to wait.

---

```python
                if retry_match and attempt < max_retries - 1:
                    retry_delay = float(retry_match.group(1))
                    print(f"      ⏳ Rate limit hit. Waiting {retry_delay:.1f}s before retry...")
                    time.sleep(retry_delay + 1)  # Add 1 second buffer
                    continue
```
> If we found a retry delay AND have retries left, wait and try again.
> Add 1 second buffer to be safe.

---

```python
                else:
                    # Daily quota exhausted - return special error
                    print(f"      ❌ Daily quota exhausted")
                    return {
                        "success": False,
                        "response": {"category": "Other", "confidence": 0.0, "reasoning": "Daily quota exhausted"},
                        "error": "QUOTA_EXHAUSTED",
                        "model": "gemini-2.0-flash"
                    }
```
> If we've used all retries or it's a daily quota issue, return special error.
> `QUOTA_EXHAUSTED` signals to the caller to stop processing more emails.

---

```python
            # Other errors - return default
            print(f"      ❌ Categorization error: {str(e)}")
            return {
                "success": False,
                "response": {"category": "Other", "confidence": 0.0, "reasoning": "Error: " + str(e)},
                "error": str(e),
                "model": "gemini-2.0-flash"
            }
```
> For any other error, return a default "Other" category with the error message.

---

## 7. extract_actions()

```python
def extract_actions(self, email: Dict[str, Any]) -> Dict[str, Any]:
    """Extract action items from email"""
    prompt = self.prompt_manager.format_prompt("action_extraction", email)
    return self.llm_client.call_llm(prompt, temperature=0.3)
```
> Extract tasks/action items from an email.
> - Get the "action_extraction" prompt template
> - Fill in email details
> - Call the LLM with low temperature (0.3) for consistent extraction
> - Uses `llm_client` (not fast_model) since this is called less frequently

---

## 8. summarize_email()

```python
def summarize_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
    """Generate email summary"""
    prompt = self.prompt_manager.format_prompt("summarization", email)
    return self.llm_client.call_llm(prompt, temperature=0.5)
```
> Generate a summary of the email.
> - Get the "summarization" prompt template
> - Fill in email details
> - Call the LLM with medium temperature (0.5) for some creativity
> - Returns summary with key points and urgency level

---

## 9. process_inbox()

```python
def process_inbox(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Process multiple emails
    
    Args:
        emails: List of email dicts
        
    Returns:
        List of processed email results
    """
    results = []
    for email in emails:
        result = self.process_email(email)
        results.append(result)
    return results
```
> Process multiple emails in a batch.
> - Loop through each email
> - Call `process_email()` for each one
> - Collect and return all results
>
> **Note:** This processes emails sequentially (not parallel) to avoid rate limits.

---

## 10. get_processed_email()

```python
def get_processed_email(self, email_id: str) -> Optional[Dict[str, Any]]:
    """Get processed data for a specific email"""
    return self.processed_emails.get(email_id)
```
> Get the processed data for a single email by ID.
> - Returns the processed data if found
> - Returns `None` if not found (that's what `.get()` does)

---

## 11. get_all_processed_emails()

```python
def get_all_processed_emails(self) -> Dict[str, Any]:
    """Get all processed emails"""
    return self.processed_emails
```
> Get all processed emails as a dictionary.
> Format: `{"email_id": processed_data, ...}`

---

## 12. get_emails_by_category()

```python
def get_emails_by_category(self, category: str) -> List[Dict[str, Any]]:
    """Get all emails in a specific category"""
    results = []
    for email_id, processed in self.processed_emails.items():
        if processed.get("category", {}).get("category") == category:
            results.append(processed)
    return results
```
> Filter processed emails by category.
> - Loop through all processed emails
> - Check if the category matches (e.g., "Urgent", "Deadline")
> - Return list of matching emails
>
> **Usage:** `processor.get_emails_by_category("Urgent")` returns all urgent emails.

---

## 13. get_all_action_items()

```python
def get_all_action_items(self) -> List[Dict[str, Any]]:
    """Get all action items across all emails"""
    all_actions = []
    for email_id, processed in self.processed_emails.items():
        actions = processed.get("action_items", [])
        for action in actions:
            action["email_id"] = email_id
            action["email_subject"] = processed["email"].get("subject")
            all_actions.append(action)
    return all_actions
```
> Get ALL action items from ALL processed emails.
> - Loop through all processed emails
> - Get each email's action items
> - Add email context (ID and subject) to each action
> - Collect into one big list
>
> **Usage:** Great for showing a "Tasks" view across the whole inbox.

---

## 📊 Visual Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                      EmailProcessor                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌───────────────┐  ┌───────────────────────┐ │
│  │  LLMClient   │  │PromptManager  │  │    fast_model         │ │
│  │  (actions,   │  │(templates)    │  │ (categorization only) │ │
│  │   summary)   │  │               │  │                       │ │
│  └──────┬───────┘  └───────┬───────┘  └───────────┬───────────┘ │
│         │                  │                      │              │
│         └──────────────────┼──────────────────────┘              │
│                            │                                     │
│                            ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      Methods                              │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  🔄 process_email()      - Full 3-step pipeline          │   │
│  │  🏷️  categorize_email()  - Classify email (fast model)   │   │
│  │  ✅ extract_actions()    - Get tasks/deadlines           │   │
│  │  📝 summarize_email()    - Create summary                │   │
│  │  📦 process_inbox()      - Batch process emails          │   │
│  │  🔍 get_processed_email()- Get one result by ID          │   │
│  │  📋 get_all_processed_emails() - Get all results         │   │
│  │  🏷️  get_emails_by_category() - Filter by category       │   │
│  │  ✅ get_all_action_items() - All tasks from all emails   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Processing Pipeline

```
                    Input Email
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     process_email()                              │
│                                                                  │
│  ┌─────────────────┐                                            │
│  │ Step 1:         │                                            │
│  │ CATEGORIZE      │──▶ Urgent / Deadline / Conversation /      │
│  │ (fast_model)    │    Spam / Other                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐                                            │
│  │ Step 2:         │    [                                       │
│  │ EXTRACT ACTIONS │──▶   { task, deadline, priority },         │
│  │ (llm_client)    │      { task, deadline, priority }          │
│  └────────┬────────┘    ]                                       │
│           │                                                      │
│           ▼                                                      │
│  ┌─────────────────┐    {                                       │
│  │ Step 3:         │      summary: "...",                       │
│  │ SUMMARIZE       │──▶   key_points: [...],                    │
│  │ (llm_client)    │      urgency: "high"                       │
│  └────────┬────────┘    }                                       │
│           │                                                      │
└───────────┼──────────────────────────────────────────────────────┘
            │
            ▼
     Store in processed_emails
            │
            ▼
      Return Result
```

---

## 🏷️ Category Types

| Category | Color | Description | Example |
|----------|-------|-------------|---------|
| **Urgent** | 🔴 Red | Critical, needs immediate attention | "URGENT: Server down!" |
| **Deadline** | 🟠 Orange | Has a specific due date | "Report due by Friday" |
| **Conversation** | 🟢 Green | Regular discussion, FYI | "Re: Team lunch plans" |
| **Spam** | ⚫ Grey | Promotional, unwanted | "50% OFF SALE!" |
| **Other** | 🟤 Brown | Doesn't fit other categories | Misc emails |

---

## 📦 Data Structures

### Processed Email Object
```json
{
  "email": {
    "id": "e001",
    "sender": "john@example.com",
    "subject": "Project Update",
    "body": "..."
  },
  "processed_at": "2025-12-18T14:30:22.123456",
  "category": {
    "category": "Deadline",
    "confidence": 0.95,
    "reasoning": "Contains due date"
  },
  "action_items": [
    {
      "task": "Review document",
      "deadline": "2025-12-20",
      "priority": "high",
      "context": "EOD Friday"
    }
  ],
  "summary": {
    "summary": "John requesting document review",
    "key_points": ["Document attached", "Due Friday"],
    "urgency": "medium",
    "requires_response": true
  },
  "processing_errors": []
}
```

### Category Response
```json
{
  "category": "Urgent",
  "confidence": 0.95,
  "reasoning": "Subject contains URGENT and mentions server issues"
}
```

### Action Items Response
```json
{
  "action_items": [
    {
      "task": "Review the attached document",
      "deadline": "2025-12-20",
      "priority": "high",
      "context": "Feedback needed by EOD Friday"
    }
  ],
  "has_actions": true
}
```

---

## ⚡ Why Two Models?

```
┌─────────────────────────────────────────────────────────────────┐
│                    Model Usage Strategy                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────┐  ┌─────────────────────────────┐   │
│  │     fast_model          │  │        llm_client           │   │
│  │  (gemini-2.0-flash)     │  │     (gemini-2.0-flash)      │   │
│  ├─────────────────────────┤  ├─────────────────────────────┤   │
│  │ Used for:               │  │ Used for:                   │   │
│  │ • Categorization only   │  │ • Action extraction         │   │
│  │                         │  │ • Summarization             │   │
│  ├─────────────────────────┤  ├─────────────────────────────┤   │
│  │ Why separate?           │  │ Why shared?                 │   │
│  │ • Bulk processing       │  │ • Less frequent calls       │   │
│  │ • Simple JSON response  │  │ • Reuses retry logic        │   │
│  │ • Custom retry logic    │  │ • Consistent with other     │   │
│  │ • Rate limit handling   │  │   parts of the app          │   │
│  └─────────────────────────┘  └─────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

**Key Insight:** Categorization is called most often (once per email in bulk mode), so it has its own model with specialized rate limit handling.

---

## 🚦 Error Handling

| Error Type | Response | Action |
|------------|----------|--------|
| **Rate Limit (429)** | Wait and retry | Extract delay from error, sleep, try again |
| **Daily Quota** | Return `QUOTA_EXHAUSTED` | Stop processing, notify user |
| **Safety Filter** | Return `Other` category | Use safe default |
| **JSON Parse Error** | Try to extract JSON | Find `{...}` in response |
| **Other Errors** | Return error in response | Log and continue |

---

## 💡 Usage Examples

```python
# Create processor
processor = EmailProcessor(llm_client, prompt_manager)

# Process single email
result = processor.process_email(email)
print(result["category"]["category"])  # "Urgent"

# Process all emails
results = processor.process_inbox(all_emails)

# Get emails by category
urgent_emails = processor.get_emails_by_category("Urgent")

# Get all tasks
tasks = processor.get_all_action_items()
for task in tasks:
    print(f"[{task['email_subject']}] {task['task']} - Due: {task['deadline']}")
```

---

*Last Updated: December 18, 2025*
