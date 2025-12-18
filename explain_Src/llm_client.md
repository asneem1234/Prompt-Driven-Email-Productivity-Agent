# 🤖 LLM Client - Explained Line by Line

> **File:** `src/llm_client.py`  
> **Purpose:** Wrapper for all Google Gemini AI API interactions  
> **Lines:** 169

---

## 📋 Table of Contents

1. [Overview](#1-overview)
2. [Imports](#2-imports)
3. [Class Definition](#3-class-definition)
4. [Constructor (__init__)](#4-constructor-__init__)
5. [call_llm()](#5-call_llm---main-api-method)
6. [get_call_history()](#6-get_call_history)
7. [clear_history()](#7-clear_history)

---

## 1. Overview

The `LLMClient` class is the **foundation** of all AI interactions in the project. It:
- 🔑 **Manages** the Gemini API key securely
- 📤 **Sends** prompts to Google Gemini AI
- 📥 **Receives** and parses JSON responses
- 🔄 **Retries** failed requests with exponential backoff
- 📜 **Logs** all API calls for debugging
- 🛡️ **Handles** rate limits, safety filters, and connection errors

**Key Design:** This is the ONLY place in the codebase that talks directly to Gemini. All other modules use this client.

---

## 2. Imports

```python
"""
LLM Client for Email Productivity Agent
Supports Google Gemini AI
"""
```
> Docstring describing the file's purpose.

---

```python
import os
```
> `os` module helps us access environment variables.
> We use it to get the `GEMINI_API_KEY` from the `.env` file.

---

```python
import json
```
> `json` module converts between Python dictionaries and JSON strings.
> The AI returns JSON text, we parse it into Python objects.

---

```python
import time
```
> `time` module lets us pause the program with `time.sleep()`.
> Used for waiting during retry attempts after rate limits.

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
import google.generativeai as genai
```
> Google's official Gemini AI library.
> This is what actually communicates with Google's servers.

---

```python
from dotenv import load_dotenv
```
> `python-dotenv` library for loading environment variables from `.env` file.
> Keeps API keys secure and out of the code.

---

```python
load_dotenv()
```
> **Execute immediately:** Read the `.env` file and load all variables.
> After this line, `os.getenv("GEMINI_API_KEY")` will work.

---

## 3. Class Definition

```python
class LLMClient:
    """Handles all LLM interactions with structured prompt/response logging"""
```
> Create the `LLMClient` class.
> All AI communication goes through this class.

---

## 4. Constructor (__init__)

```python
def __init__(self, model: str = "gemini-2.0-flash"):
```
> Constructor - runs when creating a new LLMClient.
> - `model` = which Gemini model to use (default: gemini-2.0-flash)
> - Can be changed to use other models like "gemini-pro"

---

```python
    self.api_key = os.getenv("GEMINI_API_KEY")
```
> Get the API key from environment variables.
> The key should be in your `.env` file like: `GEMINI_API_KEY=your_key_here`

---

```python
    if not self.api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
```
> **Safety check:** If no API key is found, crash immediately with a clear error.
> Better to fail fast than to have confusing errors later.

---

```python
    genai.configure(api_key=self.api_key)
```
> Configure the Google library with our API key.
> All subsequent calls will use this key automatically.

---

```python
    self.model = genai.GenerativeModel(model)
```
> Create a model instance for the specified Gemini model.
> This object will be used for all `generate_content()` calls.

---

```python
    self.call_history = []
```
> Empty list to store all API calls (both successful and failed).
> Useful for debugging and understanding what happened.

---

## 5. call_llm() - Main API Method

This is the **core method** that sends prompts to Gemini and handles responses.

```python
def call_llm(
    self, 
    prompt: str, 
    temperature: float = 0.7,
    max_tokens: int = 1000,
    json_mode: bool = True,
    max_retries: int = 3
) -> Dict[str, Any]:
```
> Call the Gemini AI with a prompt.
> 
> **Parameters:**
> - `prompt` = the text/question to send to AI
> - `temperature` = creativity level (0.0 = deterministic, 1.0 = very creative)
> - `max_tokens` = maximum response length (1 token ≈ 4 characters)
> - `json_mode` = if True, ask AI to respond in JSON format
> - `max_retries` = how many times to retry on failure

---

```python
    """
    Call LLM with the given prompt and return structured response
    
    Args:
        prompt: The formatted prompt to send
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens in response
        json_mode: Whether to request JSON response format
        max_retries: Maximum number of retry attempts for rate limits
        
    Returns:
        Dict with 'response', 'raw_response', 'prompt_used', 'success', 'error'
    """
```
> Documentation explaining the function.

---

### JSON Mode Setup

```python
    if json_mode:
        full_prompt = f"{prompt}\n\nIMPORTANT: Respond with ONLY valid JSON. No markdown, no code blocks, just pure JSON."
    else:
        full_prompt = prompt
```
> If we want JSON, append special instructions telling the AI to respond ONLY with JSON.
> This helps ensure we get parseable responses.

---

### Generation Configuration

```python
    generation_config = {
        "temperature": temperature,
        "max_output_tokens": max_tokens,
    }
```
> Create config object for Gemini.
> - `temperature` controls randomness/creativity
> - `max_output_tokens` limits response length

---

### Retry Loop

```python
    for attempt in range(max_retries):
```
> Loop up to `max_retries` times (default: 3).
> `attempt` will be 0, 1, 2 for 3 retries.

---

### API Call

```python
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config=generation_config
            )
```
> **The actual API call!**
> Send the prompt to Gemini and wait for the response.
> This is wrapped in `try` because it might fail.

---

### Safety Filter Check

```python
            if not response.candidates or not response.candidates[0].content.parts:
                finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
                return {
                    "success": False,
                    "response": None,
                    "raw_response": None,
                    "prompt_used": prompt,
                    "model": "gemini-2.0-flash",
                    "error": f"Response blocked (finish_reason: {finish_reason}). Try asking in a different way or with less context."
                }
```
> Check if Google's safety filters blocked the response.
> If blocked, `candidates` will be empty or have no content.
> Return an error explaining what happened.

---

### Get Raw Response

```python
            raw_response = response.text
```
> Extract the text content from the response object.

---

### JSON Parsing

```python
            if json_mode:
                try:
                    clean_response = raw_response.strip()
```
> If expecting JSON, start cleaning the response.
> Remove leading/trailing whitespace.

---

```python
                    if clean_response.startswith("```json"):
                        clean_response = clean_response.split("```json")[1].split("```")[0].strip()
                    elif clean_response.startswith("```"):
                        clean_response = clean_response.split("```")[1].split("```")[0].strip()
```
> AI sometimes wraps JSON in markdown code blocks.
> Extract just the JSON part.
> 
> Example: ` ```json {"key": "value"} ``` ` → `{"key": "value"}`

---

```python
                    parsed_response = json.loads(clean_response)
```
> Parse the JSON string into a Python dictionary.

---

```python
                except json.JSONDecodeError as e:
                    parsed_response = {"error": "Failed to parse JSON", "raw": raw_response, "parse_error": str(e)}
```
> If parsing fails, return an error dict with the raw response.
> This way the caller can still see what the AI returned.

---

```python
            else:
                parsed_response = {"text": raw_response}
```
> If not JSON mode, just wrap the text in a simple dict.

---

### Success Response

```python
            result = {
                "success": True,
                "response": parsed_response,
                "raw_response": raw_response,
                "prompt_used": prompt,
                "model": "gemini-2.0-flash",
                "error": None
            }
            
            self.call_history.append(result)
            return result
```
> Build the success response object with all relevant data.
> Save to history and return.

---

### Error Handling

```python
        except Exception as e:
            error_msg = str(e)
```
> Catch any exception and convert to string for analysis.

---

### Rate Limit Handling (429 Error)

```python
            if "429" in error_msg or "RATE_LIMIT_EXCEEDED" in error_msg or "Quota exceeded" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 10  # 10s, 20s, 40s
                    print(f"⏳ Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
```
> **Rate Limit:** Google limits API requests (15/minute for free tier).
> 
> **Exponential Backoff:** Wait longer each retry:
> - Attempt 0: wait 10 seconds
> - Attempt 1: wait 20 seconds
> - Attempt 2: wait 40 seconds
> 
> `continue` goes back to the start of the loop.

---

```python
                else:
                    error_msg = (
                        "⚠️ Rate limit exceeded. Gemini free tier allows 15 requests/minute. "
                        "Please wait 60 seconds and try again, or:\n"
                        "1. Upgrade to paid tier at https://ai.google.dev/pricing\n"
                        "2. Reduce number of simultaneous requests\n"
                        "3. Wait for the rate limit window to reset\n"
                        f"Original error: {error_msg}"
                    )
```
> If all retries failed, provide a helpful error message with solutions.

---

### Connection Error Handling

```python
            elif "503" in error_msg or "Timeout" in error_msg or "socket" in error_msg or "failed to connect" in error_msg:
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 5  # 5s, 10s, 20s
                    print(f"⚠️ Connection issue. Retrying in {wait_time} seconds... ({attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    error_msg = (
                        "❌ Unable to connect to Gemini API after multiple attempts. "
                        "This could be due to:\n"
                        "1. Network connectivity issues\n"
                        "2. Google API service outage\n"
                        "3. Firewall/proxy blocking the connection\n"
                        f"Original error: {error_msg}"
                    )
```
> Handle connection problems (server down, network issues).
> Shorter waits than rate limits: 5s, 10s, 20s.

---

### Return Error

```python
            result = {
                "success": False,
                "response": None,
                "raw_response": None,
                "prompt_used": prompt,
                "model": "gemini-2.0-flash",
                "error": error_msg
            }
            
            self.call_history.append(result)
            return result
```
> Build error response, save to history, and return.

---

## 6. get_call_history()

```python
def get_call_history(self) -> list:
    """Return history of all LLM calls"""
    return self.call_history
```
> Get the list of all API calls made.
> Includes both successful and failed calls.
> Useful for debugging and auditing.

---

## 7. clear_history()

```python
def clear_history(self):
    """Clear call history"""
    self.call_history = []
```
> Reset the call history to empty.
> Useful to free memory or start fresh.

---

## 📊 Visual Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                        LLMClient                                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    Properties                             │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  🔑 api_key        - Gemini API key from .env            │   │
│  │  🤖 model          - GenerativeModel instance            │   │
│  │  📜 call_history   - List of all API calls               │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                      Methods                              │   │
│  ├──────────────────────────────────────────────────────────┤   │
│  │  📤 call_llm()         - Send prompt, get response       │   │
│  │  📋 get_call_history() - Get all past calls              │   │
│  │  🗑️  clear_history()    - Reset call history             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Request Flow

```
            Prompt
               │
               ▼
┌─────────────────────────────────┐
│         call_llm()              │
├─────────────────────────────────┤
│ 1. Add JSON instructions        │
│    (if json_mode=True)          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ 2. Configure generation         │
│    • temperature                │
│    • max_output_tokens          │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ 3. Retry Loop (max 3)           │
│    ┌─────────────────────────┐  │
│    │ model.generate_content()│──┼──▶ Google Gemini API
│    └─────────────────────────┘  │
└──────────────┬──────────────────┘
               │
       ┌───────┴───────┐
       │               │
    Success         Error
       │               │
       ▼               ▼
┌─────────────┐  ┌─────────────────┐
│ Safety      │  │ Rate Limit?     │
│ Filter OK?  │  │ Connection?     │
└──────┬──────┘  └────────┬────────┘
       │                  │
       ▼                  ▼
┌─────────────┐  ┌─────────────────┐
│ Parse JSON  │  │ Wait & Retry    │
│ (if needed) │  │ (exp backoff)   │
└──────┬──────┘  └─────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│ 4. Build Result                 │
│    • success: true/false        │
│    • response: parsed data      │
│    • raw_response: text         │
│    • error: message (if any)    │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│ 5. Save to call_history         │
└──────────────┬──────────────────┘
               │
               ▼
          Return Result
```

---

## ⏱️ Exponential Backoff Explained

```
                     Rate Limit Error (429)
                              │
                              ▼
                    ┌─────────────────┐
                    │  Attempt 0      │
                    │  Wait: 10 sec   │──▶ 2^0 × 10 = 10s
                    └────────┬────────┘
                             │ Still failing?
                             ▼
                    ┌─────────────────┐
                    │  Attempt 1      │
                    │  Wait: 20 sec   │──▶ 2^1 × 10 = 20s
                    └────────┬────────┘
                             │ Still failing?
                             ▼
                    ┌─────────────────┐
                    │  Attempt 2      │
                    │  Wait: 40 sec   │──▶ 2^2 × 10 = 40s
                    └────────┬────────┘
                             │ Still failing?
                             ▼
                    ┌─────────────────┐
                    │  Give Up        │
                    │  Return Error   │
                    └─────────────────┘

Connection Errors use: 2^n × 5 = 5s, 10s, 20s
```

**Why Exponential Backoff?**
- Gives servers time to recover
- Reduces load during outages
- Required by most API rate limits

---

## 📦 Response Structure

### Successful Response
```json
{
  "success": true,
  "response": {
    "category": "Urgent",
    "confidence": 0.95,
    "reasoning": "Subject contains URGENT"
  },
  "raw_response": "{\"category\": \"Urgent\", ...}",
  "prompt_used": "Categorize this email...",
  "model": "gemini-2.0-flash",
  "error": null
}
```

### Failed Response (Rate Limit)
```json
{
  "success": false,
  "response": null,
  "raw_response": null,
  "prompt_used": "Categorize this email...",
  "model": "gemini-2.0-flash",
  "error": "⚠️ Rate limit exceeded. Gemini free tier allows 15 requests/minute..."
}
```

### Failed Response (Safety Filter)
```json
{
  "success": false,
  "response": null,
  "raw_response": null,
  "prompt_used": "...",
  "model": "gemini-2.0-flash",
  "error": "Response blocked (finish_reason: SAFETY). Try asking in a different way..."
}
```

---

## 🌡️ Temperature Guide

| Temperature | Behavior | Use Case |
|-------------|----------|----------|
| **0.0** | Deterministic, same output | Categorization |
| **0.3** | Mostly consistent | Action extraction |
| **0.5** | Balanced | Summarization |
| **0.7** | Somewhat creative | Email replies |
| **1.0** | Very creative, random | Creative writing |

---

## 🚦 Error Types & Handling

| Error | Detection | Retry? | Wait Time |
|-------|-----------|--------|-----------|
| **Rate Limit (429)** | "429", "RATE_LIMIT", "Quota" | ✅ Yes | 10s, 20s, 40s |
| **Connection** | "503", "Timeout", "socket" | ✅ Yes | 5s, 10s, 20s |
| **Safety Filter** | Empty `candidates` | ❌ No | - |
| **Other** | Any other exception | ❌ No | - |

---

## 💡 Usage Examples

### Basic Usage
```python
# Create client
client = LLMClient()

# Simple call
result = client.call_llm("What is 2+2?")

if result["success"]:
    print(result["response"])
else:
    print(f"Error: {result['error']}")
```

### With Custom Settings
```python
# More creative, longer response, no JSON
result = client.call_llm(
    prompt="Write a poem about email",
    temperature=0.9,
    max_tokens=500,
    json_mode=False
)
```

### Check History
```python
# See all calls made
for call in client.get_call_history():
    print(f"Success: {call['success']}, Prompt: {call['prompt_used'][:50]}...")

# Clear history
client.clear_history()
```

---

## 🔐 Security Notes

| Concern | Solution |
|---------|----------|
| API Key Exposure | Store in `.env` file, never commit to git |
| Key in Code | Use `os.getenv()` to read from environment |
| `.env` in Git | Add `.env` to `.gitignore` |
| Sharing Code | Provide `.env.example` without real key |

### Example `.env` file:
```env
GEMINI_API_KEY=AIzaSyB1234567890abcdefghijklmnop
```

### Example `.env.example` (safe to commit):
```env
GEMINI_API_KEY=your_api_key_here
```

---

*Last Updated: December 18, 2025*
