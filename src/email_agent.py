"""
Email Agent for Chat-based Inbox Interaction
Handles conversational queries about emails
"""
from typing import Dict, Any, List, Optional
from src.llm_client import LLMClient
from src.email_processor import EmailProcessor


class EmailAgent:
    """Conversational agent for interacting with email inbox"""
    
    def __init__(self, llm_client: LLMClient, email_processor: EmailProcessor):
        self.llm_client = llm_client
        self.email_processor = email_processor
        self.conversation_history = []
    
    def query(
        self, 
        user_query: str,
        selected_email: Optional[Dict[str, Any]] = None,
        context_emails: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process a user query about emails
        
        Args:
            user_query: The user's question or request
            selected_email: Currently selected email (if any)
            context_emails: List of emails for context
            
        Returns:
            Agent response with answer and metadata
        """
        # Build context
        context = self._build_context(selected_email, context_emails)
        
        # Create agent prompt
        prompt = f"""You are an Email Productivity Agent. Answer the user's query about their emails.

{context}

User Query: {user_query}

Provide a helpful, concise response. If the query is about a specific email, reference it clearly. If it's about multiple emails, summarize appropriately.

Respond in JSON format:
{{
  "answer": "<your response to the user>",
  "email_references": ["<email_id_1>", "<email_id_2>"],
  "suggested_actions": ["<action 1>", "<action 2>"],
  "requires_draft": <true/false>
}}"""
        
        result = self.llm_client.call_llm(prompt, temperature=0.7, max_tokens=1500)
        
        # Add to conversation history
        self.conversation_history.append({
            "query": user_query,
            "response": result.get("response"),
            "context_provided": context[:200] + "..." if len(context) > 200 else context
        })
        
        return result
    
    def _build_context(
        self,
        selected_email: Optional[Dict[str, Any]],
        context_emails: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build context string for the agent"""
        context_parts = []
        
        # Add selected email
        if selected_email:
            processed = self.email_processor.get_processed_email(selected_email.get("id"))
            if processed:
                context_parts.append("Currently Selected Email:")
                context_parts.append(f"  From: {selected_email.get('sender')}")
                context_parts.append(f"  Subject: {selected_email.get('subject')}")
                context_parts.append(f"  Category: {processed.get('category', {}).get('category', 'Unknown')}")
                context_parts.append(f"  Body Preview: {selected_email.get('body', '')[:200]}...")
                
                # Add action items if any
                actions = processed.get('action_items', [])
                if actions:
                    context_parts.append(f"  Action Items: {len(actions)} tasks found")
        
        # Add inbox summary
        all_processed = self.email_processor.get_all_processed_emails()
        if all_processed:
            context_parts.append(f"\nInbox Summary:")
            context_parts.append(f"  Total Emails: {len(all_processed)}")
            
            # Category breakdown
            categories = {}
            for email_id, processed in all_processed.items():
                cat = processed.get('category', {}).get('category', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            for cat, count in categories.items():
                context_parts.append(f"  {cat}: {count}")
            
            # Total action items
            all_actions = self.email_processor.get_all_action_items()
            context_parts.append(f"  Total Action Items: {len(all_actions)}")
        
        # Add context emails if provided
        if context_emails:
            context_parts.append(f"\nContext Emails ({len(context_emails)} emails):")
            for email in context_emails[:5]:  # Limit to 5 for context size
                context_parts.append(f"  - {email.get('subject')} (from {email.get('sender')})")
        
        return "\n".join(context_parts)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
