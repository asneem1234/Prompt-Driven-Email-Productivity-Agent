"""
Prompt Manager for Email Productivity Agent
Handles loading, saving, and formatting prompts
"""
import json
import os
from typing import Dict, Any, Optional
from datetime import datetime


class PromptManager:
    """Manages prompt templates with versioning and formatting"""
    
    def __init__(self, prompts_file: str = "data/default_prompts.json"):
        self.prompts_file = prompts_file
        self.prompts = {}
        self.prompt_history = []
        # If the deployment environment is read-only (e.g. Vercel), we'll
        # keep an in-memory copy of prompts and avoid failing when saving.
        self.read_only = False
        self._in_memory_prompts = {}
        self.load_prompts()
    
    def load_prompts(self):
        """Load prompts from JSON file"""
        try:
            if os.path.exists(self.prompts_file):
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    self.prompts = json.load(f)
            else:
                # Create default prompts if file doesn't exist
                self.prompts = self._get_default_prompts()
                try:
                    self.save_prompts()
                except OSError:
                    # If we cannot write to disk, fallback to in-memory prompts
                    self.read_only = True
                    self._in_memory_prompts = self.prompts.copy()
        except (OSError, PermissionError) as e:
            # Running in a read-only environment (e.g., serverless deployment)
            # Use an in-memory fallback so the UI still works but changes are ephemeral.
            self.read_only = True
            if not self._in_memory_prompts:
                self._in_memory_prompts = self._get_default_prompts()
            self.prompts = self._in_memory_prompts.copy()
    
    def save_prompts(self):
        """Save prompts to JSON file"""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.prompts_file), exist_ok=True)
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(self.prompts, f, indent=2, ensure_ascii=False)
            # Add to history
            self.prompt_history.append({
                "timestamp": datetime.now().isoformat(),
                "prompts": self.prompts.copy()
            })
            # If we previously thought filesystem was read-only, reset that flag
            self.read_only = False
        except (OSError, PermissionError) as e:
            # Filesystem is not writable (common on serverless platforms)
            # Fallback to in-memory storage so users can still edit prompts in the UI.
            self.read_only = True
            self._in_memory_prompts = self.prompts.copy()
            # Record history even for in-memory saves
            self.prompt_history.append({
                "timestamp": datetime.now().isoformat(),
                "prompts": self.prompts.copy(),
                "note": "saved-in-memory"
            })
    
    def get_prompt(self, prompt_type: str) -> Optional[Dict[str, Any]]:
        """Get a specific prompt by type"""
        return self.prompts.get(prompt_type)
    
    def update_prompt(self, prompt_type: str, prompt_data: Dict[str, Any]):
        """Update a prompt template"""
        self.prompts[prompt_type] = prompt_data
        # Attempt to persist; if running in read-only environment this will
        # fallback to an in-memory store and set `self.read_only`.
        try:
            self.save_prompts()
        except Exception:
            # Save failure already handled inside save_prompts; just ensure
            # prompts are available in-memory for the session.
            self._in_memory_prompts = self.prompts.copy()
    
    def format_prompt(self, prompt_type: str, email_data: Dict[str, Any]) -> str:
        """
        Format a prompt template with email data
        
        Args:
            prompt_type: Type of prompt (categorization, action_extraction, etc.)
            email_data: Email data dict with sender, subject, body
            
        Returns:
            Formatted prompt string
        """
        prompt_template = self.prompts.get(prompt_type)
        if not prompt_template:
            raise ValueError(f"Prompt type '{prompt_type}' not found")
        
        template = prompt_template.get("prompt", "")
        
        # Replace placeholders manually to avoid issues with JSON braces in template
        formatted_prompt = template.replace("{sender}", email_data.get("sender", "Unknown"))
        formatted_prompt = formatted_prompt.replace("{subject}", email_data.get("subject", "No Subject"))
        formatted_prompt = formatted_prompt.replace("{body}", email_data.get("body", ""))
        
        return formatted_prompt
    
    def get_all_prompts(self) -> Dict[str, Any]:
        """Get all prompts"""
        return self.prompts
    
    def get_prompt_history(self) -> list:
        """Get prompt version history"""
        return self.prompt_history
    
    def _get_default_prompts(self) -> Dict[str, Any]:
        """Return default prompt templates"""
        return {
            "categorization": {
                "name": "Email Categorization",
                "prompt": "Categorize this email: From: {sender}, Subject: {subject}, Body: {body}",
                "description": "Categorizes emails"
            },
            "action_extraction": {
                "name": "Action Item Extraction",
                "prompt": "Extract action items from: {body}",
                "description": "Extracts tasks"
            },
            "auto_reply": {
                "name": "Auto-Reply Generator",
                "prompt": "Generate reply for: {body}",
                "description": "Generates replies"
            }
        }
