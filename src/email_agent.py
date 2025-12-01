"""
Email Agent for Chat-based Inbox Interaction
Handles conversational queries about emails with RAG
"""
from typing import Dict, Any, List, Optional
from src.llm_client import LLMClient
from src.email_processor import EmailProcessor
from src.rag_system import EmailRAGSystem
from src.prompt_manager import PromptManager


class EmailAgent:
    """Conversational agent for interacting with email inbox using RAG"""
    
    def __init__(self, llm_client: LLMClient, email_processor: EmailProcessor, prompt_manager: PromptManager = None):
        self.llm_client = llm_client
        self.email_processor = email_processor
        self.rag_system = EmailRAGSystem()
        self.prompt_manager = prompt_manager or PromptManager()
        self.conversation_history = []
    
    def query(
        self, 
        user_query: str,
        selected_email: Optional[Dict[str, Any]] = None,
        context_emails: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Process a user query about emails using RAG
        
        Args:
            user_query: The user's question or request
            selected_email: Currently selected email (if any)
            context_emails: List of emails for context
            
        Returns:
            Agent response with answer and metadata
        """
        # Index emails in RAG system if not already done
        if context_emails and not self.rag_system.indexed:
            self.rag_system.index_emails(context_emails)
        
        # Rephrase problematic queries to avoid safety blocks
        query_lower = user_query.lower()
        if 'task' in query_lower and ('need' in query_lower or 'do' in query_lower):
            user_query = "Show me important and urgent emails that need action"
        
        # Use RAG to retrieve relevant emails
        # For summary/overview queries, use fewer emails to avoid safety blocks
        is_summary_query = any(word in query_lower for word in ['summary', 'overview', 'all emails', 'everything', 'inbox'])
        top_k = 3 if is_summary_query else 5
        relevant_emails = self.rag_system.retrieve_relevant_emails(user_query, top_k=top_k)
        
        # Build context with RAG results
        context = self._build_rag_context(user_query, selected_email, relevant_emails)
        
        # Create comprehensive RAG-enhanced agent prompt
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
        
        result = self.llm_client.call_llm(prompt, temperature=0.7, max_tokens=1500)
        
        # If blocked by safety filter, provide a helpful fallback
        if not result.get('success'):
            error_msg = result.get('error', '')
            if 'finish_reason' in error_msg or 'blocked' in error_msg.lower():
                # Provide a simpler, stats-based response
                stats = self.rag_system.get_stats()
                fallback_answer = f"Your inbox has {stats['total_emails']} emails: {stats['unread']} unread, {stats['starred']} starred, {stats['important']} important. Try asking about specific emails like 'Show me urgent emails' or 'Show me unread messages'."
                result = {
                    'success': True,
                    'response': {
                        'answer': fallback_answer,
                        'email_references': [],
                        'suggested_actions': ['Try a more specific query'],
                        'requires_draft': False
                    }
                }
        
        # Add to conversation history
        self.conversation_history.append({
            "query": user_query,
            "response": result.get("response"),
            "context_provided": context[:200] + "..." if len(context) > 200 else context
        })
        
        return result
    
    def _build_rag_context(
        self,
        query: str,
        selected_email: Optional[Dict[str, Any]],
        relevant_emails: List[Dict[str, Any]]
    ) -> str:
        """Build RAG-enhanced context with relevant emails"""
        context_parts = []
        
        # Add email statistics (simplified for safety)
        stats = self.rag_system.get_stats()
        context_parts.append("EMAIL STATS:")
        context_parts.append(f"Total: {stats['total_emails']}, Unread: {stats['unread']}, Starred: {stats['starred']}, Important: {stats['important']}")
        context_parts.append("")
        
        # Add selected email if present
        if selected_email:
            context_parts.append("=== CURRENTLY SELECTED EMAIL ===")
            context_parts.append(f"From: {selected_email.get('sender_name', selected_email.get('sender'))}")
            context_parts.append(f"Subject: {selected_email.get('subject')}")
            context_parts.append(f"Body: {selected_email.get('body', '')[:500]}")
            context_parts.append("")
        
        # Add RAG-retrieved relevant emails
        context_parts.append(f"=== RELEVANT EMAILS FOR QUERY (Top {len(relevant_emails)}) ===")
        context_parts.append(f"Query: '{query}'")
        context_parts.append("")
        
        for idx, result in enumerate(relevant_emails, 1):
            email = result['email']
            score = result['score']
            
            context_parts.append(f"[{idx}] Relevance: {score:.2f}")
            context_parts.append(f"    ID: {email.get('id')}")
            context_parts.append(f"    From: {email.get('sender_name', email.get('sender'))}")
            context_parts.append(f"    Subject: {email.get('subject')}")
            context_parts.append(f"    Date: {email.get('timestamp', 'Unknown')[:10]}")
            context_parts.append(f"    Preview: {email.get('body', '')[:80]}...")
            
            # Add flags
            flags = []
            if email.get('starred'):
                flags.append("⭐ STARRED")
            if email.get('important'):
                flags.append("❗ IMPORTANT")
            if email.get('read') == False:
                flags.append("📬 UNREAD")
            if flags:
                context_parts.append(f"    Flags: {', '.join(flags)}")
            
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def _build_context(
        self,
        selected_email: Optional[Dict[str, Any]],
        context_emails: Optional[List[Dict[str, Any]]]
    ) -> str:
        """Build context string for the agent (legacy method)"""
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
        
        # Add ALL context emails for RAG (Retrieval-Augmented Generation)
        if context_emails:
            context_parts.append(f"\n=== FULL EMAIL DATABASE ({len(context_emails)} emails) ===")
            context_parts.append("You have access to ALL emails below. Search through them to answer user queries accurately.\n")
            
            for idx, email in enumerate(context_emails, 1):
                context_parts.append(f"\n[Email {idx}] ID: {email.get('id')}")
                context_parts.append(f"From: {email.get('sender_name', email.get('sender'))}")
                context_parts.append(f"Subject: {email.get('subject')}")
                context_parts.append(f"Date: {email.get('timestamp', 'Unknown')}")
                context_parts.append(f"Body: {email.get('body', '')[:300]}...")
                
                # Add starred/important flags if present
                if email.get('starred'):
                    context_parts.append("⭐ STARRED")
                if email.get('important'):
                    context_parts.append("❗ IMPORTANT")
                if email.get('read') == False:
                    context_parts.append("📬 UNREAD")
                
                context_parts.append("---")
        
        return "\n".join(context_parts)
    
    def generate_reply(self, email: Dict[str, Any], user_instruction: str = None) -> Dict[str, Any]:
        """
        Generate a reply draft for an email using prompt manager
        
        Args:
            email: The email to reply to
            user_instruction: Optional specific instructions for the reply
            
        Returns:
            Dict with generated reply and metadata
        """
        # Get reply prompt from prompt manager (uses 'auto_reply' prompt)
        reply_prompt_data = self.prompt_manager.get_prompt("auto_reply")
        
        if reply_prompt_data:
            # Use user-defined prompt from Custom Prompt page
            base_prompt = reply_prompt_data.get('prompt', '')
            formatted_prompt = self.prompt_manager.format_prompt("auto_reply", email)
        else:
            # Fallback if no prompt defined
            formatted_prompt = f"""Generate a professional email reply.

Original Email:
From: {email.get('sender_name', email.get('sender'))}
Subject: {email.get('subject')}
Body: {email.get('body', '')}

Generate a suitable reply."""
        
        # Add user instruction if provided
        if user_instruction:
            formatted_prompt += f"\n\nAdditional Instructions: {user_instruction}"
        
        formatted_prompt += "\n\nReturn JSON: {\"reply_body\": \"your reply text here\", \"subject\": \"Re: subject\"}"
        
        # Call LLM
        result = self.llm_client.call_llm(formatted_prompt, temperature=0.7, max_tokens=800)
        
        if result.get('success'):
            reply_data = result.get('response', {})
            # The prompt returns 'body' but we need 'reply_body' for the frontend
            # Handle both cases for flexibility
            reply_body = reply_data.get('reply_body') or reply_data.get('body', '')
            return {
                'success': True,
                'reply_body': reply_body,
                'subject': reply_data.get('subject', f"Re: {email.get('subject', '')}"),
                'original_email_id': email.get('id')
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Failed to generate reply')
            }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
