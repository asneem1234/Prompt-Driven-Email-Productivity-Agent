# 🔍 RAG System - Explained Line by Line

> **File:** `src/rag_system.py`  
> **Purpose:** Retrieval-Augmented Generation system for semantic email search  
> **Lines:** 247

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [Imports](#2-imports)
3. [Class Definition](#3-class-definition)
4. [Constructor (__init__)](#4-constructor-__init__)
5. [index_emails()](#5-index_emails)
6. [_create_email_text()](#6-_create_email_text)
7. [_create_embedding()](#7-_create_embedding)
8. [retrieve_relevant_emails()](#8-retrieve_relevant_emails)
9. [_calculate_similarity()](#9-_calculate_similarity)
10. [_has_keywords()](#10-_has_keywords)
11. [_matches_filters()](#11-_matches_filters)
12. [Convenience Search Methods](#12-convenience-search-methods)
13. [get_stats()](#13-get_stats)

---

## 1. Overview

**RAG** stands for **Retrieval-Augmented Generation**. It's a technique that:
1. **Retrieves** relevant documents (emails) based on a query
2. **Augments** the AI prompt with those documents
3. **Generates** a response using the retrieved context

This system enables the chat agent to:
- 🔍 Find emails related to user questions
- 📊 Provide accurate answers with specific email references
- 🎯 Filter by sender, starred status, read/unread, etc.

**Key Design:** Uses a **lightweight keyword-based** approach instead of heavy neural embeddings. This keeps the system fast and doesn't require external ML models.

---

## 2. Imports

```python
"""
RAG (Retrieval-Augmented Generation) System for Email Agent
Uses semantic search to find relevant emails for user queries
"""
```
> Module docstring explaining the file's purpose.

---

```python
import numpy as np
```
> `numpy` for numerical operations (though not heavily used here).
> Could be used for vector operations in future enhancements.

---

```python
from typing import Dict, Any, List, Tuple
```
> Type hints for better code documentation:
> - `Dict` = dictionary
> - `Any` = any type
> - `List` = list
> - `Tuple` = tuple (fixed-size ordered collection)

---

```python
import json
```
> `json` module for potential serialization (available but not actively used).

---

```python
import re
```
> `re` = Regular Expressions for text processing.
> Used to extract words from text.

---

## 3. Class Definition

```python
class EmailRAGSystem:
    """RAG system with semantic search for emails"""
```
> Create the `EmailRAGSystem` class.
> This is the search engine for emails.

---

## 4. Constructor (__init__)

```python
def __init__(self):
    self.emails = []
```
> Initialize empty list to store all emails.

---

```python
    self.email_embeddings = {}
```
> Dictionary to store processed email data.
> Format: `{email_id: {text, embedding, email}}`

---

```python
    self.indexed = False
```
> Flag to track if emails have been indexed.
> Prevents searching before indexing.

---

## 5. index_emails()

This method **prepares emails for searching**.

```python
def index_emails(self, emails: List[Dict[str, Any]]):
    """
    Index emails for RAG retrieval
    Creates searchable representations of each email
    """
```
> Takes a list of email dictionaries and indexes them.

---

```python
    self.emails = emails
    self.email_embeddings = {}
```
> Store emails and reset embeddings dictionary.

---

```python
    for email in emails:
        email_id = email.get('id')
```
> Loop through each email and get its unique ID.

---

```python
        # Create rich text representation for embedding
        email_text = self._create_email_text(email)
```
> Convert the email to searchable text format.
> Combines sender, subject, body, date, flags into one string.

---

```python
        # Create simple keyword-based embedding (lightweight approach)
        embedding = self._create_embedding(email_text)
```
> Create the "embedding" - a dictionary of word frequencies.
> This is what we search against.

---

```python
        self.email_embeddings[email_id] = {
            'text': email_text,
            'embedding': embedding,
            'email': email
        }
```
> Store everything indexed by email ID:
> - `text` = searchable string
> - `embedding` = word frequency dictionary
> - `email` = original email data

---

```python
    self.indexed = True
    print(f"✅ RAG System indexed {len(emails)} emails")
```
> Mark indexing complete and log success.

---

## 6. _create_email_text()

Converts an email object into a **searchable text string**.

```python
def _create_email_text(self, email: Dict[str, Any]) -> str:
    """Create searchable text representation of email"""
    parts = []
```
> Create empty list to collect text parts.

---

```python
    # Add all searchable fields
    parts.append(f"From: {email.get('sender_name', '')} {email.get('sender', '')}")
    parts.append(f"Subject: {email.get('subject', '')}")
    parts.append(f"Body: {email.get('body', '')}")
    parts.append(f"Date: {email.get('timestamp', '')}")
```
> Add core email fields with labels:
> - From (name + email address)
> - Subject line
> - Email body
> - Timestamp

---

```python
    # Add flags
    if email.get('starred'):
        parts.append("STARRED IMPORTANT")
    if email.get('important'):
        parts.append("IMPORTANT PRIORITY")
    if email.get('read') == False:
        parts.append("UNREAD NEW")
```
> Add flag keywords so users can search by status:
> - "Show starred emails" → finds "STARRED"
> - "Unread messages" → finds "UNREAD"

---

```python
    # Add folder
    folder = email.get('folder', 'inbox')
    parts.append(f"Folder: {folder}")
```
> Add folder name for folder-based searches.

---

```python
    return " ".join(parts).lower()
```
> Join all parts with spaces and convert to lowercase.
> Lowercase makes searching case-insensitive.

---

## 7. _create_embedding()

Creates a **word frequency dictionary** (our "embedding").

```python
def _create_embedding(self, text: str) -> Dict[str, float]:
    """
    Create a simple keyword-based embedding
    This is lightweight and doesn't require external models
    """
```
> Creates a simple representation instead of neural embeddings.
> No GPU or external AI models needed!

---

```python
    # Extract keywords and their frequencies
    words = re.findall(r'\b\w+\b', text.lower())
```
> Use regex to find all words:
> - `\b` = word boundary
> - `\w+` = one or more word characters
> - `\b` = word boundary
> 
> Example: `"Hello, world!"` → `["hello", "world"]`

---

```python
    # Create frequency-based embedding
    embedding = {}
    for word in words:
        if len(word) > 2:  # Skip very short words
            embedding[word] = embedding.get(word, 0) + 1
```
> Count how many times each word appears.
> Skip words with 2 or fewer characters (like "a", "to", "is").
> 
> Example: `"the meeting about the project"` → `{"the": 2, "meeting": 1, "about": 1, "project": 1}`

---

```python
    return embedding
```
> Return the word frequency dictionary.

---

## 8. retrieve_relevant_emails()

The **main search method** - finds emails matching a query.

```python
def retrieve_relevant_emails(
    self, 
    query: str, 
    top_k: int = 10,
    filters: Dict[str, Any] = None
) -> List[Dict[str, Any]]:
```
> Parameters:
> - `query` = what the user is searching for
> - `top_k` = how many results to return (default 10)
> - `filters` = optional filters (sender, starred, etc.)

---

```python
    """
    Retrieve most relevant emails for a query using semantic search
    
    Args:
        query: User's search query
        top_k: Number of emails to return
        filters: Optional filters (sender, starred, unread, etc.)
        
    Returns:
        List of relevant emails with relevance scores
    """
```
> Detailed docstring explaining the method.

---

```python
    if not self.indexed:
        return []
```
> Safety check: return empty if not indexed yet.

---

```python
    # Create query embedding
    query_embedding = self._create_embedding(query.lower())
```
> Convert the user's query to the same format as email embeddings.
> This allows comparison.

---

```python
    # Calculate similarity scores for all emails
    scores = []
    for email_id, data in self.email_embeddings.items():
```
> Loop through all indexed emails to score them.

---

```python
        # Calculate similarity
        score = self._calculate_similarity(query_embedding, data['embedding'])
```
> Calculate how similar the query is to this email.
> Uses cosine similarity (explained below).

---

```python
        # Apply keyword boost
        if self._has_keywords(query.lower(), data['text']):
            score *= 1.5
```
> **Bonus points** if the email contains exact query keywords.
> Multiplies score by 1.5 (50% boost).

---

```python
        # Apply filters
        if filters:
            if not self._matches_filters(data['email'], filters):
                continue
```
> Skip emails that don't match the filters.
> `continue` = skip to next email in loop.

---

```python
        scores.append({
            'email': data['email'],
            'score': score,
            'email_id': email_id
        })
```
> Add this email to results with its score.

---

```python
    # Sort by relevance score
    scores.sort(key=lambda x: x['score'], reverse=True)
```
> Sort by score, highest first.
> `reverse=True` = descending order.

---

```python
    # Return top_k results
    return scores[:top_k]
```
> Return only the top K results (default 10).

---

## 9. _calculate_similarity()

Calculates **cosine similarity** between query and email.

```python
def _calculate_similarity(
    self, 
    query_emb: Dict[str, float], 
    doc_emb: Dict[str, float]
) -> float:
    """Calculate cosine similarity between query and document"""
```
> Cosine similarity measures the angle between two vectors.
> Result is between 0 (no match) and 1 (perfect match).

---

```python
    if not query_emb or not doc_emb:
        return 0.0
```
> Return 0 if either embedding is empty.

---

```python
    # Calculate dot product
    dot_product = 0
    for word, freq in query_emb.items():
        if word in doc_emb:
            dot_product += freq * doc_emb[word]
```
> **Dot product**: Multiply matching word frequencies and sum.
> Only words that appear in BOTH query AND email contribute.

---

```python
    # Calculate magnitudes
    query_mag = sum(f * f for f in query_emb.values()) ** 0.5
    doc_mag = sum(f * f for f in doc_emb.values()) ** 0.5
```
> **Magnitude**: The "length" of each vector.
> Formula: √(sum of squared frequencies)
> `** 0.5` = square root

---

```python
    if query_mag == 0 or doc_mag == 0:
        return 0.0
```
> Avoid division by zero.

---

```python
    return dot_product / (query_mag * doc_mag)
```
> **Cosine similarity formula:**
> ```
> similarity = (A · B) / (|A| × |B|)
> ```
> This normalizes the score so longer documents don't automatically win.

---

## 10. _has_keywords()

Checks if email contains **query keywords**.

```python
def _has_keywords(self, query: str, text: str) -> bool:
    """Check if text contains query keywords"""
    query_words = set(re.findall(r'\b\w+\b', query.lower()))
```
> Extract unique words from the query.
> `set()` removes duplicates.

---

```python
    # Check for exact phrase match
    if query in text:
        return True
```
> If the exact query phrase appears, return True immediately.
> Example: Query "project meeting" found in "about the project meeting tomorrow"

---

```python
    # Check for keyword matches
    matches = sum(1 for word in query_words if word in text)
    return matches >= max(1, len(query_words) * 0.5)
```
> Count how many query words appear in the text.
> Return True if at least 50% of query words match.
> `max(1, ...)` ensures at least 1 match is required.

---

## 11. _matches_filters()

Checks if an email **passes all filters**.

```python
def _matches_filters(self, email: Dict[str, Any], filters: Dict[str, Any]) -> bool:
    """Check if email matches given filters"""
```
> Returns True if email matches ALL filters.

---

```python
    if filters.get('sender'):
        if filters['sender'].lower() not in email.get('sender', '').lower():
            return False
```
> **Sender filter:** Check if sender contains the filter text.
> Case-insensitive comparison.

---

```python
    if filters.get('starred') is not None:
        if email.get('starred') != filters['starred']:
            return False
```
> **Starred filter:** Check starred status.
> `is not None` because we want to match `False` too.

---

```python
    if filters.get('unread') is not None:
        if email.get('read') == filters['unread']:  # Note: read is opposite of unread
            return False
```
> **Unread filter:** Note the inverted logic!
> `read=True` means NOT unread.

---

```python
    if filters.get('important') is not None:
        if email.get('important') != filters['important']:
            return False
```
> **Important filter:** Check important flag.

---

```python
    if filters.get('folder'):
        if email.get('folder') != filters['folder']:
            return False
```
> **Folder filter:** Check folder name.

---

```python
    return True
```
> If all filters pass, return True.

---

## 12. Convenience Search Methods

These are **shortcut methods** for common searches.

### search_by_sender()
```python
def search_by_sender(self, sender: str, top_k: int = 10) -> List[Dict[str, Any]]:
    """Search emails by sender"""
    return self.retrieve_relevant_emails(
        query=f"from {sender}",
        top_k=top_k,
        filters={'sender': sender}
    )
```
> Find emails from a specific sender.
> Uses both query matching AND sender filter.

---

### search_by_keywords()
```python
def search_by_keywords(self, keywords: List[str], top_k: int = 10) -> List[Dict[str, Any]]:
    """Search emails by keywords"""
    query = " ".join(keywords)
    return self.retrieve_relevant_emails(query=query, top_k=top_k)
```
> Search by a list of keywords.
> Joins keywords into a single query string.

---

### get_unread_emails()
```python
def get_unread_emails(self) -> List[Dict[str, Any]]:
    """Get all unread emails"""
    return [email for email in self.emails if email.get('read') == False]
```
> Get all unread emails using list comprehension.
> No scoring needed - just filtering.

---

### get_starred_emails()
```python
def get_starred_emails(self) -> List[Dict[str, Any]]:
    """Get all starred emails"""
    return [email for email in self.emails if email.get('starred') == True]
```
> Get all starred emails.

---

### get_important_emails()
```python
def get_important_emails(self) -> List[Dict[str, Any]]:
    """Get all important emails"""
    return [email for email in self.emails if email.get('important') == True]
```
> Get all emails marked as important.

---

## 13. get_stats()

Returns **statistics** about the email collection.

```python
def get_stats(self) -> Dict[str, Any]:
    """Get email statistics"""
    total = len(self.emails)
    unread = len(self.get_unread_emails())
    starred = len(self.get_starred_emails())
    important = len(self.get_important_emails())
```
> Count basic statistics using the helper methods.

---

```python
    # Count by sender
    senders = {}
    for email in self.emails:
        sender = email.get('sender_name', email.get('sender', 'Unknown'))
        senders[sender] = senders.get(sender, 0) + 1
```
> Count emails per sender.
> Build a dictionary: `{"John": 5, "Alice": 3, ...}`

---

```python
    # Count by folder
    folders = {}
    for email in self.emails:
        folder = email.get('folder', 'inbox')
        folders[folder] = folders.get(folder, 0) + 1
```
> Count emails per folder.
> Build a dictionary: `{"inbox": 10, "sent": 5, ...}`

---

```python
    return {
        'total_emails': total,
        'unread': unread,
        'starred': starred,
        'important': important,
        'top_senders': sorted(senders.items(), key=lambda x: x[1], reverse=True)[:5],
        'folders': folders
    }
```
> Return comprehensive stats:
> - Total, unread, starred, important counts
> - Top 5 senders (sorted by count, descending)
> - Emails per folder

---

## 📊 Visual Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                     EmailRAGSystem                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Properties                             │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  📧 emails           - List of all emails                │   │
│  │  🔢 email_embeddings - {id: {text, embedding, email}}    │   │
│  │  ✅ indexed          - Has indexing been done?           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Core Methods                           │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  📥 index_emails()           - Prepare emails for search │   │
│  │  🔍 retrieve_relevant_emails() - Main search method      │   │
│  │  📄 _create_email_text()     - Email → searchable text   │   │
│  │  🔢 _create_embedding()      - Text → word frequencies   │   │
│  │  📐 _calculate_similarity()  - Cosine similarity         │   │
│  │  🔑 _has_keywords()          - Keyword matching          │   │
│  │  🎯 _matches_filters()       - Filter validation         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                  Convenience Methods                      │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  👤 search_by_sender()       - Find by sender            │   │
│  │  🔑 search_by_keywords()     - Find by keywords          │   │
│  │  📬 get_unread_emails()      - Get unread list           │   │
│  │  ⭐ get_starred_emails()     - Get starred list          │   │
│  │  ❗ get_important_emails()   - Get important list        │   │
│  │  📊 get_stats()              - Get statistics            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 RAG Search Flow

```
        User Query: "emails from John about the meeting"
                              │
                              ▼
                   ┌─────────────────────┐
                   │  Create Query       │
                   │  Embedding          │
                   │                     │
                   │  {"emails": 1,      │
                   │   "from": 1,        │
                   │   "john": 1,        │
                   │   "about": 1,       │
                   │   "meeting": 1}     │
                   └──────────┬──────────┘
                              │
                              ▼
       ┌─────────────────────────────────────────────┐
       │         For Each Email in Index              │
       ├─────────────────────────────────────────────┤
       │                                              │
       │  1. Calculate cosine similarity              │
       │     query embedding ←→ email embedding       │
       │                                              │
       │  2. Boost score if keywords match (+50%)     │
       │                                              │
       │  3. Apply filters (sender, starred, etc.)    │
       │                                              │
       │  4. Add to results list with score           │
       │                                              │
       └─────────────────────────────────────────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  Sort by Score      │
                   │  (highest first)    │
                   └──────────┬──────────┘
                              │
                              ▼
                   ┌─────────────────────┐
                   │  Return Top K       │
                   │  Results            │
                   └─────────────────────┘
```

---

## 📐 Cosine Similarity Explained

```
  Query: "project meeting"
  Email: "Let's discuss the project in our team meeting tomorrow"

  Query Embedding:                Email Embedding:
  {"project": 1, "meeting": 1}    {"let": 1, "discuss": 1, "project": 1,
                                   "team": 1, "meeting": 1, "tomorrow": 1}

                    ┌─────────────────────────────────────┐
                    │         Cosine Similarity           │
                    ├─────────────────────────────────────┤
                    │                                     │
                    │  Dot Product:                       │
                    │  project: 1 × 1 = 1                 │
                    │  meeting: 1 × 1 = 1                 │
                    │  Total: 2                           │
                    │                                     │
                    │  Query Magnitude: √(1² + 1²) = √2   │
                    │  Doc Magnitude: √(6) ≈ 2.45         │
                    │                                     │
                    │  Similarity = 2 / (√2 × 2.45)       │
                    │             ≈ 0.58                  │
                    │                                     │
                    └─────────────────────────────────────┘
```

---

## 🔑 Why Keyword-Based Instead of Neural Embeddings?

| Approach | Pros | Cons |
|----------|------|------|
| **Keyword-Based (This system)** | Fast, no dependencies, works offline, lightweight | Less semantic understanding |
| **Neural Embeddings** | Better semantic matching, understands synonyms | Requires ML models, slower, more resources |

This system prioritizes:
- ⚡ **Speed** - No ML inference needed
- 📦 **Simplicity** - No external model dependencies
- 🌐 **Portability** - Works anywhere Python runs

---

## 💡 Usage Examples

### Index Emails
```python
rag = EmailRAGSystem()
emails = [
    {"id": 1, "sender": "john@example.com", "subject": "Meeting", "body": "..."},
    {"id": 2, "sender": "alice@example.com", "subject": "Report", "body": "..."},
]
rag.index_emails(emails)
# Output: ✅ RAG System indexed 2 emails
```

### Search with Query
```python
results = rag.retrieve_relevant_emails("project deadline")
for result in results:
    print(f"Score: {result['score']:.2f} - {result['email']['subject']}")
```

### Search with Filters
```python
results = rag.retrieve_relevant_emails(
    query="budget",
    filters={"starred": True, "folder": "inbox"}
)
```

### Get Statistics
```python
stats = rag.get_stats()
print(f"Total: {stats['total_emails']}, Unread: {stats['unread']}")
print(f"Top Sender: {stats['top_senders'][0]}")
```

---

## 🏗️ Embedding Structure

```python
email_embeddings = {
    "email_001": {
        "text": "from: john smith john@example.com subject: project update...",
        "embedding": {
            "john": 2,
            "smith": 1,
            "project": 3,
            "update": 1,
            "meeting": 2,
            ...
        },
        "email": {
            "id": "email_001",
            "sender": "john@example.com",
            "subject": "Project Update",
            "body": "...",
            ...
        }
    },
    "email_002": { ... },
    ...
}
```

---

## 📈 Stats Output Structure

```python
{
    "total_emails": 50,
    "unread": 12,
    "starred": 8,
    "important": 5,
    "top_senders": [
        ("John Smith", 10),
        ("Alice Johnson", 8),
        ("Bob Williams", 6),
        ("HR Department", 5),
        ("Newsletter", 4)
    ],
    "folders": {
        "inbox": 35,
        "sent": 10,
        "drafts": 3,
        "trash": 2
    }
}
```

---

## 🔗 Integration with EmailAgent

```
┌─────────────────────────────────────────────────────────────────┐
│                        EmailAgent                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User: "What did John say about the budget?"                    │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              RAG System                                  │    │
│  │                                                          │    │
│  │  1. retrieve_relevant_emails("John budget")             │    │
│  │  2. Returns top 5 matching emails                       │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              LLM Client                                  │    │
│  │                                                          │    │
│  │  Prompt: "Based on these emails: [email context]         │    │
│  │           Answer: What did John say about the budget?"   │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                           │                                      │
│                           ▼                                      │
│  AI: "In John's email on Dec 15, he mentioned the budget        │
│       needs to be finalized by end of month..."                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📂 File Location

```
project/
├── src/
│   ├── rag_system.py       ◀── This file
│   └── email_agent.py      ◀── Uses RAG system
├── data/
│   └── mock_inbox.json     ◀── Emails to index
└── ...
```

---

*Last Updated: December 18, 2025*
