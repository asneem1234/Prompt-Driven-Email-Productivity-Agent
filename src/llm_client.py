"""
LLM Client for Email Productivity Agent
Supports OpenAI and other LLM providers
"""
import os
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    """Handles all LLM interactions with structured prompt/response logging"""
    
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.call_history = []
    
    def call_llm(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 1000,
        json_mode: bool = True
    ) -> Dict[str, Any]:
        """
        Call LLM with the given prompt and return structured response
        
        Args:
            prompt: The formatted prompt to send
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            json_mode: Whether to request JSON response format
            
        Returns:
            Dict with 'response', 'raw_response', 'prompt_used', 'success', 'error'
        """
        try:
            response_format = {"type": "json_object"} if json_mode else None
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful email productivity assistant. Always respond with valid JSON when requested."},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format=response_format
            )
            
            raw_response = completion.choices[0].message.content
            
            # Try to parse JSON response
            if json_mode:
                try:
                    parsed_response = json.loads(raw_response)
                except json.JSONDecodeError:
                    parsed_response = {"error": "Failed to parse JSON", "raw": raw_response}
            else:
                parsed_response = {"text": raw_response}
            
            result = {
                "success": True,
                "response": parsed_response,
                "raw_response": raw_response,
                "prompt_used": prompt,
                "model": self.model,
                "error": None
            }
            
            # Log the call
            self.call_history.append(result)
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "response": None,
                "raw_response": None,
                "prompt_used": prompt,
                "model": self.model,
                "error": str(e)
            }
            self.call_history.append(error_result)
            return error_result
    
    def get_call_history(self) -> list:
        """Return history of all LLM calls"""
        return self.call_history
    
    def clear_history(self):
        """Clear call history"""
        self.call_history = []
