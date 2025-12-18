"""
LLM Client for Email Productivity Agent
Supports Google Gemini AI
"""

import os
# os module helps us access environment variables and system stuff

import json
# json module helps us convert Python objects to JSON strings and vice versa

import time
# time module lets us pause the program (sleep) when needed

from typing import Dict, Any, Optional
# These are type hints - they help us specify what types our functions expect and return

import google.generativeai as genai
# This is Google's official library to talk to the Gemini AI model

from dotenv import load_dotenv
# dotenv helps us load secret keys from a .env file

load_dotenv()
# This reads the .env file and loads all variables into the environment


class LLMClient:
    """Handles all LLM interactions with structured prompt/response logging"""
    # This class is the main wrapper for talking to Gemini AI
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        # Constructor - runs when we create a new LLMClient object
        # model parameter lets us choose which Gemini model to use (default is gemini-2.5-flash)
        
        self.api_key = os.getenv("GEMINI_API_KEY")
        # Get the API key from environment variables (stored in .env file)
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
            # If no API key is found, stop and show an error message
        
        genai.configure(api_key=self.api_key)
        # Tell the Google library to use our API key for all requests
        
        self.model = genai.GenerativeModel(model)
        # Create a model instance that we'll use to generate responses
        
        self.call_history = []
        # Empty list to store all the calls we make (useful for debugging)
    
    def call_llm(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 1000,
        json_mode: bool = True,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        # Main function to send a prompt to the AI and get a response
        # prompt: the text/question we want to send
        # temperature: how creative the AI should be (0=focused, 1=creative)
        # max_tokens: maximum length of the response
        # json_mode: if True, ask AI to respond in JSON format
        # max_retries: how many times to retry if something fails
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
        
        if json_mode:
            # If we want JSON response, add special instructions to the prompt
            full_prompt = f"{prompt}\n\nIMPORTANT: Respond with ONLY valid JSON. No markdown, no code blocks, just pure JSON."
            # This tells the AI to only return JSON, nothing else
        else:
            full_prompt = prompt
            # Otherwise just use the original prompt as-is
        
        generation_config = {
            "temperature": temperature,
            # Controls randomness - lower = more predictable, higher = more creative
            "max_output_tokens": max_tokens,
            # Limits how long the response can be
        }
        
        for attempt in range(max_retries):
            # Loop that tries up to max_retries times if something fails
            # attempt will be 0, 1, 2 for max_retries=3
            
            try:
                # Try to make the API call (might fail due to network, rate limits, etc.)
                
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                # Send the prompt to Gemini and get the response
                
                if not response.candidates or not response.candidates[0].content.parts:
                    # Check if the response was blocked by Google's safety filters
                    # If blocked, there won't be any content in the response
                    
                    finish_reason = response.candidates[0].finish_reason if response.candidates else "UNKNOWN"
                    # Get the reason why it was blocked (or "UNKNOWN" if we can't tell)
                    
                    return {
                        "success": False,
                        "response": None,
                        "raw_response": None,
                        "prompt_used": prompt,
                        "model": "gemini-2.5-flash",
                        "error": f"Response blocked (finish_reason: {finish_reason}). Try asking in a different way or with less context."
                    }
                    # Return an error result explaining the response was blocked
                
                raw_response = response.text
                # Get the actual text response from the AI
                
                if json_mode:
                    # If we asked for JSON, try to parse it
                    
                    try:
                        clean_response = raw_response.strip()
                        # Remove any whitespace from the beginning and end
                        
                        if clean_response.startswith("```json"):
                            clean_response = clean_response.split("```json")[1].split("```")[0].strip()
                            # If AI wrapped response in ```json ... ```, extract just the JSON part
                            
                        elif clean_response.startswith("```"):
                            clean_response = clean_response.split("```")[1].split("```")[0].strip()
                            # If AI wrapped response in ``` ... ```, extract just the content
                        
                        parsed_response = json.loads(clean_response)
                        # Convert the JSON string into a Python dictionary
                        
                    except json.JSONDecodeError as e:
                        # If JSON parsing fails, return an error with the raw response
                        parsed_response = {"error": "Failed to parse JSON", "raw": raw_response, "parse_error": str(e)}
                else:
                    parsed_response = {"text": raw_response}
                    # If not JSON mode, just wrap the text in a simple dictionary
                
                result = {
                    "success": True,
                    # Mark this as a successful call
                    "response": parsed_response,
                    # The parsed response (dictionary)
                    "raw_response": raw_response,
                    # The original text from the AI (before parsing)
                    "prompt_used": prompt,
                    # The prompt we sent (useful for debugging)
                    "model": "gemini-2.5-flash",
                    # Which model we used
                    "error": None
                    # No error since it succeeded
                }
                
                self.call_history.append(result)
                # Save this call to our history list for later reference
                
                return result
                # Return the successful result and exit the function
                
            except Exception as e:
                # Something went wrong - could be network error, rate limit, etc.
                
                error_msg = str(e)
                # Convert the error to a string so we can check what went wrong
                
                if "429" in error_msg or "RATE_LIMIT_EXCEEDED" in error_msg or "Quota exceeded" in error_msg:
                    # 429 is the HTTP code for "too many requests" - we're being rate limited
                    
                    if attempt < max_retries - 1:
                        # If we haven't used all our retries yet, wait and try again
                        
                        wait_time = (2 ** attempt) * 10
                        # Exponential backoff: wait 10s, then 20s, then 40s
                        # This gives the rate limit time to reset
                        
                        print(f"⏳ Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                        # Tell the user we're waiting
                        
                        time.sleep(wait_time)
                        # Pause the program for wait_time seconds
                        
                        continue
                        # Go back to the start of the loop and try again
                    else:
                        # We've used all our retries, give up with a helpful message
                        error_msg = (
                            "⚠️ Rate limit exceeded. Gemini free tier allows 15 requests/minute. "
                            "Please wait 60 seconds and try again, or:\n"
                            "1. Upgrade to paid tier at https://ai.google.dev/pricing\n"
                            "2. Reduce number of simultaneous requests\n"
                            "3. Wait for the rate limit window to reset\n"
                            f"Original error: {error_msg}"
                        )
                
                elif "503" in error_msg or "Timeout" in error_msg or "socket" in error_msg or "failed to connect" in error_msg:
                    # These errors mean we couldn't connect to Google's servers
                    
                    if attempt < max_retries - 1:
                        # If we haven't used all retries, wait and try again
                        
                        wait_time = (2 ** attempt) * 5
                        # Shorter wait for connection issues: 5s, 10s, 20s
                        
                        print(f"⚠️ Connection issue. Retrying in {wait_time} seconds... ({attempt + 1}/{max_retries})")
                        time.sleep(wait_time)
                        continue
                        # Try again
                    else:
                        # All retries failed, give up with helpful error
                        error_msg = (
                            "❌ Unable to connect to Gemini API after multiple attempts. "
                            "This could be due to:\n"
                            "1. Network connectivity issues\n"
                            "2. Google API service outage\n"
                            "3. Firewall/proxy blocking the connection\n"
                            f"Original error: {error_msg}"
                        )
                
                result = {
                    "success": False,
                    # Mark this as a failed call
                    "response": None,
                    "raw_response": None,
                    "prompt_used": prompt,
                    "model": "gemini-2.5-flash",
                    "error": error_msg
                    # Include the error message so caller knows what went wrong
                }
                
                self.call_history.append(result)
                # Save even failed calls to history (helps with debugging)
                
                return result
                # Return the error result
    
    def get_call_history(self) -> list:
        """Return history of all LLM calls"""
        # This function lets us see all the calls we've made (both successful and failed)
        return self.call_history
    
    def clear_history(self):
        """Clear call history"""
        # This function empties the call history (useful to free up memory)
        self.call_history = []
