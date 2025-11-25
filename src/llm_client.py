"""
LLM Client for Email Productivity Agent
Supports Google Gemini AI
"""
import os
import json
import time
from typing import Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Handles all LLM interactions with structured prompt/response logging"""
    
    def __init__(self, model: str = "gemini-2.5-flash"):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
        self.call_history = []
    
    def call_llm(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 1000,
        json_mode: bool = True,
        max_retries: int = 3
    ) -> Dict[str, Any]:
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
        # Add JSON instruction if needed
        if json_mode:
            full_prompt = f"{prompt}\n\nIMPORTANT: Respond with ONLY valid JSON. No markdown, no code blocks, just pure JSON."
        else:
            full_prompt = prompt
        
        # Configure generation
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
        }
        
        # Retry logic for rate limiting
        for attempt in range(max_retries):
            try:
                # Call Gemini
                response = self.model.generate_content(
                    full_prompt,
                    generation_config=generation_config
                )
                
                raw_response = response.text
                
                # Try to parse JSON response
                if json_mode:
                    try:
                        # Clean response (remove markdown if present)
                        clean_response = raw_response.strip()
                        if clean_response.startswith("```json"):
                            clean_response = clean_response.split("```json")[1].split("```")[0].strip()
                        elif clean_response.startswith("```"):
                            clean_response = clean_response.split("```")[1].split("```")[0].strip()
                        
                        parsed_response = json.loads(clean_response)
                    except json.JSONDecodeError as e:
                        parsed_response = {"error": "Failed to parse JSON", "raw": raw_response, "parse_error": str(e)}
                else:
                    parsed_response = {"text": raw_response}
                
                result = {
                    "success": True,
                    "response": parsed_response,
                    "raw_response": raw_response,
                    "prompt_used": prompt,
                    "model": "gemini-2.5-flash",
                    "error": None
                }
                
                # Log the call
                self.call_history.append(result)
                
                return result
                
            except Exception as e:
                error_msg = str(e)
                
                # Check if it's a rate limit error
                if "429" in error_msg or "RATE_LIMIT_EXCEEDED" in error_msg or "Quota exceeded" in error_msg:
                    if attempt < max_retries - 1:
                        # Wait before retrying (longer wait for rate limits)
                        wait_time = (2 ** attempt) * 10  # 10, 20, 40 seconds
                        print(f"⏳ Rate limit hit. Waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}...")
                        time.sleep(wait_time)
                        continue
                    else:
                        error_msg = (
                            "⚠️ Rate limit exceeded. Gemini free tier allows 15 requests/minute. "
                            "Please wait 60 seconds and try again, or:\n"
                            "1. Upgrade to paid tier at https://ai.google.dev/pricing\n"
                            "2. Reduce number of simultaneous requests\n"
                            "3. Wait for the rate limit window to reset\n"
                            f"Original error: {error_msg}"
                        )
                
                result = {
                    "success": False,
                    "response": None,
                    "raw_response": None,
                    "prompt_used": prompt,
                    "model": "gemini-2.5-flash",
                    "error": error_msg
                }
                self.call_history.append(result)
                return result
    
    def get_call_history(self) -> list:
        """Return history of all LLM calls"""
        return self.call_history
    
    def clear_history(self):
        """Clear call history"""
        self.call_history = []
