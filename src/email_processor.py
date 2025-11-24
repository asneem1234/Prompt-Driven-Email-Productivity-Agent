"""
Email Processor for Email Productivity Agent
Handles email ingestion, categorization, and action extraction
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from src.llm_client import LLMClient
from src.prompt_manager import PromptManager


class EmailProcessor:
    """Processes emails through LLM pipeline for categorization and extraction"""
    
    def __init__(self, llm_client: LLMClient, prompt_manager: PromptManager):
        self.llm_client = llm_client
        self.prompt_manager = prompt_manager
        self.processed_emails = {}
    
    def process_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single email through the full pipeline
        
        Args:
            email: Email dict with id, sender, subject, body, etc.
            
        Returns:
            Processed email with category, actions, summary
        """
        email_id = email.get("id")
        
        # Initialize processed data
        processed = {
            "email": email,
            "processed_at": datetime.now().isoformat(),
            "category": None,
            "action_items": [],
            "summary": None,
            "processing_errors": []
        }
        
        # Step 1: Categorize email
        try:
            category_result = self.categorize_email(email)
            if category_result["success"]:
                processed["category"] = category_result["response"]
        except Exception as e:
            processed["processing_errors"].append(f"Categorization error: {str(e)}")
        
        # Step 2: Extract action items
        try:
            actions_result = self.extract_actions(email)
            if actions_result["success"]:
                processed["action_items"] = actions_result["response"].get("action_items", [])
        except Exception as e:
            processed["processing_errors"].append(f"Action extraction error: {str(e)}")
        
        # Step 3: Generate summary
        try:
            summary_result = self.summarize_email(email)
            if summary_result["success"]:
                processed["summary"] = summary_result["response"]
        except Exception as e:
            processed["processing_errors"].append(f"Summarization error: {str(e)}")
        
        # Store processed email
        self.processed_emails[email_id] = processed
        
        return processed
    
    def categorize_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize email using LLM"""
        prompt = self.prompt_manager.format_prompt("categorization", email)
        return self.llm_client.call_llm(prompt, temperature=0.3)
    
    def extract_actions(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Extract action items from email"""
        prompt = self.prompt_manager.format_prompt("action_extraction", email)
        return self.llm_client.call_llm(prompt, temperature=0.3)
    
    def summarize_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Generate email summary"""
        prompt = self.prompt_manager.format_prompt("summarization", email)
        return self.llm_client.call_llm(prompt, temperature=0.5)
    
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
    
    def get_processed_email(self, email_id: str) -> Optional[Dict[str, Any]]:
        """Get processed data for a specific email"""
        return self.processed_emails.get(email_id)
    
    def get_all_processed_emails(self) -> Dict[str, Any]:
        """Get all processed emails"""
        return self.processed_emails
    
    def get_emails_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all emails in a specific category"""
        results = []
        for email_id, processed in self.processed_emails.items():
            if processed.get("category", {}).get("category") == category:
                results.append(processed)
        return results
    
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
