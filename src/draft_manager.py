"""
Draft Manager for Email Productivity Agent
Handles draft generation and storage (never sends emails)
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.llm_client import LLMClient
from src.prompt_manager import PromptManager


class DraftManager:
    """Manages email draft generation and storage"""
    
    def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager):
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.drafts = {}
        self.drafts_file = "data/drafts.json"
        self.load_drafts()
    
    def load_drafts(self):
        """Load saved drafts from file"""
        if os.path.exists(self.drafts_file):
            with open(self.drafts_file, 'r', encoding='utf-8') as f:
                self.drafts = json.load(f)
    
    def save_drafts(self):
        """Save drafts to file"""
        os.makedirs(os.path.dirname(self.drafts_file), exist_ok=True)
        with open(self.drafts_file, 'w', encoding='utf-8') as f:
            json.dump(self.drafts, f, indent=2, ensure_ascii=False)
    
    def generate_reply_draft(
        self, 
        original_email: Dict[str, Any],
        custom_instructions: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a reply draft for an email
        
        Args:
            original_email: The email to reply to
            custom_instructions: Optional custom instructions for the reply
            
        Returns:
            Draft data with subject, body, metadata
        """
        # Format the auto-reply prompt
        prompt = self.prompt_manager.format_prompt("auto_reply", original_email)
        
        # Add custom instructions if provided
        if custom_instructions:
            prompt += f"\n\nAdditional Instructions: {custom_instructions}"
        
        # Call LLM
        result = self.llm_client.call_llm(prompt, temperature=0.7)
        
        if not result["success"]:
            return {
                "success": False,
                "error": result["error"],
                "draft": None
            }
        
        # Create draft object
        draft = {
            "id": f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "original_email_id": original_email.get("id"),
            "in_reply_to": {
                "sender": original_email.get("sender"),
                "subject": original_email.get("subject")
            },
            "draft_content": result["response"],
            "prompt_used": result["prompt_used"],
            "status": "draft",  # Always draft, never sent
            "custom_instructions": custom_instructions
        }
        
        # Save draft
        self.drafts[draft["id"]] = draft
        self.save_drafts()
        
        return {
            "success": True,
            "draft": draft,
            "error": None
        }
    
    def generate_new_email_draft(
        self,
        recipient: str,
        subject: str,
        context: str,
        tone: str = "professional"
    ) -> Dict[str, Any]:
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
        # Create custom prompt for new email
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
        
        result = self.llm_client.call_llm(prompt, temperature=0.7)
        
        if not result["success"]:
            return {
                "success": False,
                "error": result["error"],
                "draft": None
            }
        
        # Create draft object
        draft = {
            "id": f"draft_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "type": "new",
            "recipient": recipient,
            "draft_content": result["response"],
            "prompt_used": result["prompt_used"],
            "status": "draft",
            "context": context
        }
        
        # Save draft
        self.drafts[draft["id"]] = draft
        self.save_drafts()
        
        return {
            "success": True,
            "draft": draft,
            "error": None
        }
    
    def get_draft(self, draft_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific draft by ID"""
        return self.drafts.get(draft_id)
    
    def get_all_drafts(self) -> List[Dict[str, Any]]:
        """Get all drafts"""
        return list(self.drafts.values())
    
    def update_draft(self, draft_id: str, updates: Dict[str, Any]):
        """Update a draft"""
        if draft_id in self.drafts:
            self.drafts[draft_id].update(updates)
            self.drafts[draft_id]["updated_at"] = datetime.now().isoformat()
            self.save_drafts()
    
    def delete_draft(self, draft_id: str):
        """Delete a draft"""
        if draft_id in self.drafts:
            del self.drafts[draft_id]
            self.save_drafts()
    
    def export_draft_as_text(self, draft_id: str) -> str:
        """Export draft as formatted text"""
        draft = self.drafts.get(draft_id)
        if not draft:
            return ""
        
        content = draft.get("draft_content", {})
        
        export_text = f"""Draft Email
{'='*50}
Created: {draft.get('created_at')}
Status: {draft.get('status')}

"""
        
        if "in_reply_to" in draft:
            export_text += f"""In Reply To:
  From: {draft['in_reply_to'].get('sender')}
  Subject: {draft['in_reply_to'].get('subject')}

"""
        
        export_text += f"""Subject: {content.get('subject', 'No Subject')}

Body:
{content.get('body', '')}

"""
        
        if content.get('suggested_actions'):
            export_text += f"""Suggested Follow-ups:
"""
            for action in content.get('suggested_actions', []):
                export_text += f"  - {action}\n"
        
        return export_text
