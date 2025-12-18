# 🤖 Email Agent - Explained Line by Line

> **File:** `src/email_agent.py`  
> **Purpose:** Conversational chat agent for interacting with email inbox using RAG  
> **Lines:** 307

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [Imports](#2-imports)
3. [Class Definition](#3-class-definition)
4. [Constructor (__init__)](#4-constructor-__init__)
5. [query()](#5-query---main-chat-method)
6. [_build_rag_context()](#6-_build_rag_context)
7. [_build_context()](#7-_build_context---legacy-method)
8. [generate_reply()](#8-generate_reply)
9. [get_conversation_history()](#9-get_conversation_history)
10. [clear_history()](#10-clear_history)

---

## 1. Overview

The `EmailAgent` class is the **brain** of the chat interface. It:
- 💬 Processes natural language questions about emails
- 🔍 Uses **RAG (Retrieval-Augmented Generation)** to find relevant emails
- 🤖 Sends context + query to Gemini AI for intelligent responses
- ✉️ Generates email reply drafts
- 📜 Maintains conversation history

**Key Feature:** Instead of sending ALL emails to the AI (expensive!), it uses RAG to find only the most relevant emails first.

---

## 2. Imports

```python
"""
Email Agent for Chat-based Inbox Interaction
Handles conversational queries about emails with RAG
"""
```
> Docstring describing the file's purpose.

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
from src.llm_client import LLMClient
```
> Import the AI client that talks to Gemini.

---

```python
from src.email_processor import EmailProcessor
```
> Import the email processor for getting processed email data.

---

```python
from src.rag_system import EmailRAGSystem
```
> Import the RAG system for semantic email search.

---

```python
from src.prompt_manager import PromptManager
```
> Import the prompt manager for loading prompt templates.

---

## 3. Class Definition

```python
class EmailAgent:
    """Conversational agent for interacting with email inbox using RAG"""
```
> Create the `EmailAgent` class. This is the main chat handler.

---

## 4. Constructor (__init__)

```python
def __init__(self, llm_client: LLMClient, email_processor: EmailProcessor, prompt_manager: PromptManager = None):
```
> Constructor - runs when creating a new EmailAgent.
> - `llm_client` = the AI client for Gemini calls
> - `email_processor` = processes emails (categorization, etc.)
> - `prompt_manager` = optional, for managing prompts (has a default)

---

```python
    self.llm_client = llm_client
```
> Store the AI client for later use.

---

```python
    self.email_processor = email_processor
```
> Store the email processor.

---

```python
    self.rag_system = EmailRAGSystem()
```
> Create a NEW RAG system instance for semantic search.
> This is created fresh (not passed in) because it's internal to the agent.

---

```python
    self.prompt_manager = prompt_manager or PromptManager()
```
> Use the provided prompt manager, OR create a new one if none was given.
> The `or` operator returns the first "truthy" value.

---

```python
    self.conversation_history = []
```
> Empty list to store chat history (user questions + AI responses).

---

## 5. query() - Main Chat Method

This is the **most important method** - it handles all user questions!

```python
def query(
    self, 
    user_query: str,
    selected_email: Optional[Dict[str, Any]] = None,
    context_emails: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
```
> Process a user's question about their emails.
> - `user_query` = what the user asked (e.g., "Show me urgent emails")
> - `selected_email` = the email user is currently viewing (if any)
> - `context_emails` = all emails in the inbox for RAG search

---

```python
    """
    Process a user query about emails using RAG
    
    Args:
        user_query: The user's question or request
        selected_email: Currently selected email (if any)
        context_emails: List of emails for context
        
    Returns:
        Agent response with answer and metadata
    """
```
> Documentation explaining the function.

---

```python
    if context_emails and not self.rag_system.indexed:
        self.rag_system.index_emails(context_emails)
```
> **First time setup:** If we have emails AND haven't indexed them yet,
> index them in the RAG system for searching.
> This only happens once (lazy initialization).

---

```python
    query_lower = user_query.lower()
```
> Convert query to lowercase for easier comparison.

---

```python
    if 'task' in query_lower and ('need' in query_lower or 'do' in query_lower):
        user_query = "Show me important and urgent emails that need action"
```
> **Safety workaround:** Some queries like "What tasks do I need to do?" 
> can trigger AI safety filters. We rephrase them to avoid blocks.

---

```python
    is_summary_query = any(word in query_lower for word in ['summary', 'overview', 'all emails', 'everything', 'inbox'])
```
> Check if the user wants a summary/overview of their inbox.
> `any()` returns True if ANY of those words are in the query.

---

```python
    top_k = 3 if is_summary_query else 5
```
> For summary queries, get fewer emails (3) to avoid AI safety blocks.
> For specific queries, get more emails (5) for better answers.

---

```python
    relevant_emails = self.rag_system.retrieve_relevant_emails(user_query, top_k=top_k)
```
> **RAG Search:** Find the most relevant emails for this query.
> This is the magic - instead of sending ALL emails, we send only the relevant ones!

---

```python
    context = self._build_rag_context(user_query, selected_email, relevant_emails)
```
> Build a formatted context string with email stats, selected email, and relevant emails.

---

```python
    prompt = f"""You are an intelligent email analysis assistant. When a user asks about specific emails or points to emails in their inbox, analyze them thoroughly and provide detailed information.

Your capabilities include:
1. **Email Parsing**: Extract sender, subject, date, body content, and metadata
2. **Information Extraction**: Identify key details like:
   - Action items and deadlines
   - Important dates and times
   - Names, companies, and contact information
   - Financial information (amounts, invoice numbers, payment details)
   - Meeting invitations and event details
3. **Content Summarization**: Provide concise summaries of email content
4. **Sentiment Analysis**: Determine the tone (urgent, casual, formal, etc.)
5. **Categorization**: Classify emails (work, personal, billing, notifications, etc.)
6. **Thread Context**: Understand email conversations and reply chains
7. **Smart Responses**: Suggest appropriate reply options

Email Data:
{context}

User Query: {user_query}

When responding:
- Be concise but thorough
- Highlight the most important information first
- Use bullet points (•) for clarity
- Reference emails by ID (e.g., "Email e007")
- Flag urgent items with ⚠️
- Identify deadlines with 📅
- Mark action items with ✓
- Use plain text only - no HTML or markdown

Return JSON format:
{{
  "answer": "your detailed response here",
  "email_references": ["email_id"],
  "suggested_actions": ["action"],
  "requires_draft": false
}}"""
```
> **The Master Prompt:** This tells the AI:
> 1. What it is (email assistant)
> 2. What it can do (7 capabilities listed)
> 3. The email context (from RAG)
> 4. The user's question
> 5. How to format the response
> 6. What JSON structure to return
>
> Note: `{{` and `}}` are escaped braces (show as `{` and `}` in output).

---

```python
    result = self.llm_client.call_llm(prompt, temperature=0.7, max_tokens=1500)
```
> Send the prompt to Gemini AI.
> - `temperature=0.7` = moderately creative responses
> - `max_tokens=1500` = allow longer responses for detailed answers

---

```python
    if not result.get('success'):
        error_msg = result.get('error', '')
        if 'finish_reason' in error_msg or 'blocked' in error_msg.lower():
```
> Check if the response was blocked by safety filters.

---

```python
            stats = self.rag_system.get_stats()
            fallback_answer = f"Your inbox has {stats['total_emails']} emails: {stats['unread']} unread, {stats['starred']} starred, {stats['important']} important. Try asking about specific emails like 'Show me urgent emails' or 'Show me unread messages'."
```
> **Fallback response:** If AI was blocked, provide basic inbox stats instead.
> Better than showing an error!

---

```python
            result = {
                'success': True,
                'response': {
                    'answer': fallback_answer,
                    'email_references': [],
                    'suggested_actions': ['Try a more specific query'],
                    'requires_draft': False
                }
            }
```
> Create a fake "success" result with the fallback answer.

---

```python
    self.conversation_history.append({
        "query": user_query,
        "response": result.get("response"),
        "context_provided": context[:200] + "..." if len(context) > 200 else context
    })
```
> Save this conversation to history.
> Only save first 200 chars of context to save memory.

---

```python
    return result
```
> Return the AI's response (or fallback).

---

## 6. _build_rag_context()

This method creates the context string that gets sent to the AI.

```python
def _build_rag_context(
    self,
    query: str,
    selected_email: Optional[Dict[str, Any]],
    relevant_emails: List[Dict[str, Any]]
) -> str:
    """Build RAG-enhanced context with relevant emails"""
```
> Build a formatted string with email data for the AI.
> The underscore prefix `_` indicates this is a "private" method (internal use).

---

```python
    context_parts = []
```
> Start with an empty list. We'll build the context piece by piece.

---

```python
    stats = self.rag_system.get_stats()
    context_parts.append("EMAIL STATS:")
    context_parts.append(f"Total: {stats['total_emails']}, Unread: {stats['unread']}, Starred: {stats['starred']}, Important: {stats['important']}")
    context_parts.append("")
```
> Add inbox statistics at the top. Gives AI an overview.

---

```python
    if selected_email:
        context_parts.append("=== CURRENTLY SELECTED EMAIL ===")
        context_parts.append(f"From: {selected_email.get('sender_name', selected_email.get('sender'))}")
        context_parts.append(f"Subject: {selected_email.get('subject')}")
        context_parts.append(f"Body: {selected_email.get('body', '')[:500]}")
        context_parts.append("")
```
> If user has an email open, include its details.
> Limit body to 500 chars to save tokens.

---

```python
    context_parts.append(f"=== RELEVANT EMAILS FOR QUERY (Top {len(relevant_emails)}) ===")
    context_parts.append(f"Query: '{query}'")
    context_parts.append("")
```
> Header for the RAG results section.

---

```python
    for idx, result in enumerate(relevant_emails, 1):
        email = result['email']
        score = result['score']
```
> Loop through each relevant email.
> `enumerate(..., 1)` starts counting at 1 instead of 0.

---

```python
        context_parts.append(f"[{idx}] Relevance: {score:.2f}")
        context_parts.append(f"    ID: {email.get('id')}")
        context_parts.append(f"    From: {email.get('sender_name', email.get('sender'))}")
        context_parts.append(f"    Subject: {email.get('subject')}")
        context_parts.append(f"    Date: {email.get('timestamp', 'Unknown')[:10]}")
        context_parts.append(f"    Preview: {email.get('body', '')[:80]}...")
```
> Add each email's details with its relevance score.
> `{score:.2f}` formats the score to 2 decimal places.

---

```python
        flags = []
        if email.get('starred'):
            flags.append("⭐ STARRED")
        if email.get('important'):
            flags.append("❗ IMPORTANT")
        if email.get('read') == False:
            flags.append("📬 UNREAD")
        if flags:
            context_parts.append(f"    Flags: {', '.join(flags)}")
```
> Add visual flags (emojis) for important email attributes.

---

```python
        context_parts.append("")
    
    return "\n".join(context_parts)
```
> Join all parts with newlines and return the complete context string.

---

## 7. _build_context() - Legacy Method

```python
def _build_context(
    self,
    selected_email: Optional[Dict[str, Any]],
    context_emails: Optional[List[Dict[str, Any]]]
) -> str:
    """Build context string for the agent (legacy method)"""
```
> This is an **older method** that sends ALL emails to the AI.
> Kept for backwards compatibility but `_build_rag_context` is preferred.

---

```python
    context_parts = []
    
    if selected_email:
        processed = self.email_processor.get_processed_email(selected_email.get("id"))
        if processed:
            context_parts.append("Currently Selected Email:")
            context_parts.append(f"  From: {selected_email.get('sender')}")
            context_parts.append(f"  Subject: {selected_email.get('subject')}")
            context_parts.append(f"  Category: {processed.get('category', {}).get('category', 'Unknown')}")
            context_parts.append(f"  Body Preview: {selected_email.get('body', '')[:200]}...")
```
> Add selected email with its processed category.

---

```python
            actions = processed.get('action_items', [])
            if actions:
                context_parts.append(f"  Action Items: {len(actions)} tasks found")
```
> If email has action items, mention how many.

---

```python
    all_processed = self.email_processor.get_all_processed_emails()
    if all_processed:
        context_parts.append(f"\nInbox Summary:")
        context_parts.append(f"  Total Emails: {len(all_processed)}")
```
> Add inbox summary with total count.

---

```python
        categories = {}
        for email_id, processed in all_processed.items():
            cat = processed.get('category', {}).get('category', 'Unknown')
            categories[cat] = categories.get(cat, 0) + 1
        
        for cat, count in categories.items():
            context_parts.append(f"  {cat}: {count}")
```
> Count emails by category and display breakdown.

---

```python
        all_actions = self.email_processor.get_all_action_items()
        context_parts.append(f"  Total Action Items: {len(all_actions)}")
```
> Show total action items across all emails.

---

```python
    if context_emails:
        context_parts.append(f"\n=== FULL EMAIL DATABASE ({len(context_emails)} emails) ===")
        context_parts.append("You have access to ALL emails below. Search through them to answer user queries accurately.\n")
        
        for idx, email in enumerate(context_emails, 1):
            context_parts.append(f"\n[Email {idx}] ID: {email.get('id')}")
            context_parts.append(f"From: {email.get('sender_name', email.get('sender'))}")
            context_parts.append(f"Subject: {email.get('subject')}")
            context_parts.append(f"Date: {email.get('timestamp', 'Unknown')}")
            context_parts.append(f"Body: {email.get('body', '')[:300]}...")
```
> Add ALL emails - this is expensive and why we prefer RAG!

---

```python
            if email.get('starred'):
                context_parts.append("⭐ STARRED")
            if email.get('important'):
                context_parts.append("❗ IMPORTANT")
            if email.get('read') == False:
                context_parts.append("📬 UNREAD")
            
            context_parts.append("---")
    
    return "\n".join(context_parts)
```
> Add flags and separators, then return the full context.

---

## 8. generate_reply()

```python
def generate_reply(self, email: Dict[str, Any], user_instruction: str = None) -> Dict[str, Any]:
    """
    Generate a reply draft for an email using prompt manager
    
    Args:
        email: The email to reply to
        user_instruction: Optional specific instructions for the reply
        
    Returns:
        Dict with generated reply and metadata
    """
```
> Generate an AI reply to an email.

---

```python
    reply_prompt_data = self.prompt_manager.get_prompt("auto_reply")
```
> Get the "auto_reply" prompt template from the prompt manager.

---

```python
    if reply_prompt_data:
        base_prompt = reply_prompt_data.get('prompt', '')
        formatted_prompt = self.prompt_manager.format_prompt("auto_reply", email)
```
> If we have a custom prompt, use it and fill in email details.

---

```python
    else:
        formatted_prompt = f"""Generate a professional email reply.

Original Email:
From: {email.get('sender_name', email.get('sender'))}
Subject: {email.get('subject')}
Body: {email.get('body', '')}

Generate a suitable reply."""
```
> Fallback prompt if no custom prompt is defined.

---

```python
    if user_instruction:
        formatted_prompt += f"\n\nAdditional Instructions: {user_instruction}"
```
> Add any user-specified instructions (e.g., "be more formal").

---

```python
    formatted_prompt += "\n\nReturn JSON: {\"reply_body\": \"your reply text here\", \"subject\": \"Re: subject\"}"
```
> Tell AI to return JSON format.

---

```python
    result = self.llm_client.call_llm(formatted_prompt, temperature=0.7, max_tokens=800)
```
> Call Gemini with the prompt.

---

```python
    if result.get('success'):
        reply_data = result.get('response', {})
        reply_body = reply_data.get('reply_body') or reply_data.get('body', '')
        return {
            'success': True,
            'reply_body': reply_body,
            'subject': reply_data.get('subject', f"Re: {email.get('subject', '')}"),
            'original_email_id': email.get('id')
        }
```
> On success, extract the reply and return it.
> Handle both `reply_body` and `body` keys for flexibility.

---

```python
    else:
        return {
            'success': False,
            'error': result.get('error', 'Failed to generate reply')
        }
```
> On failure, return the error.

---

## 9. get_conversation_history()

```python
def get_conversation_history(self) -> List[Dict[str, Any]]:
    """Get conversation history"""
    return self.conversation_history
```
> Return the list of all past queries and responses.
> Useful for showing chat history in the UI.

---

## 10. clear_history()

```python
def clear_history(self):
    """Clear conversation history"""
    self.conversation_history = []
```
> Reset the conversation history to empty.
> Called when user clicks "Clear Chat".

---

## 📊 Visual Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                        EmailAgent                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌───────────────┐  ┌───────────────────────┐ │
│  │  LLMClient   │  │EmailProcessor │  │    RAGSystem          │ │
│  │  (AI calls)  │  │(email data)   │  │ (semantic search)     │ │
│  └──────┬───────┘  └───────┬───────┘  └───────────┬───────────┘ │
│         │                  │                      │              │
│         └──────────────────┼──────────────────────┘              │
│                            │                                     │
│                            ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      Methods                              │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  💬 query()              - Answer questions about emails  │   │
│  │  📋 _build_rag_context() - Build context from RAG results│   │
│  │  📋 _build_context()     - Legacy full-context builder   │   │
│  │  ↩️  generate_reply()     - Create email reply draft      │   │
│  │  📜 get_conversation_history() - Get chat history        │   │
│  │  🗑️  clear_history()      - Reset conversation           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Query Flow (RAG Process)

```
User: "Show me urgent emails"
              │
              ▼
┌─────────────────────────┐
│ 1. Index Emails (once)  │
│    rag_system.index()   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 2. Rephrase if needed   │
│    (safety workaround)  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 3. RAG Search           │
│    retrieve_relevant()  │──▶ Returns Top 5 emails
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 4. Build Context        │
│    _build_rag_context() │──▶ Stats + Selected + Relevant
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 5. Create Master Prompt │
│    (capabilities +      │
│     context + query)    │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 6. Call Gemini AI       │
│    llm_client.call_llm()│
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 7. Handle Response      │
│    (or fallback)        │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 8. Save to History      │
└───────────┬─────────────┘
            │
            ▼
      Return Result
```

---

## 🔍 RAG vs Full Context Comparison

| Aspect | RAG (Current) | Full Context (Legacy) |
|--------|---------------|----------------------|
| **Emails Sent** | Top 3-5 relevant | ALL emails |
| **Token Usage** | Low (~2000) | High (~10000+) |
| **Speed** | Fast | Slow |
| **Cost** | Cheap | Expensive |
| **Accuracy** | High (focused) | Medium (overwhelmed) |
| **Safety Blocks** | Fewer | More common |

---

## 📦 Response Structure

```json
{
  "success": true,
  "response": {
    "answer": "You have 3 urgent emails:\n• Email e007: Server Maintenance Tonight\n• Email e005: Security Update\n• Email e012: Deadline Tomorrow",
    "email_references": ["e007", "e005", "e012"],
    "suggested_actions": [
      "Review server maintenance email",
      "Check security update details"
    ],
    "requires_draft": false
  }
}
```

---

## 💡 Key Concepts

### What is RAG?
**Retrieval-Augmented Generation** is a technique where:
1. First, we **retrieve** relevant documents (emails) using search
2. Then, we **augment** the AI prompt with those documents
3. Finally, we **generate** a response using the AI

This is better than sending all data because:
- ✅ Uses fewer tokens (cheaper)
- ✅ More focused responses
- ✅ Faster processing
- ✅ Fewer safety filter blocks

### Why Conversation History?
- Shows chat context in the UI
- Could be used for multi-turn conversations
- Helps with debugging

---

*Last Updated: December 18, 2025*
