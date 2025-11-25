"""
Email Agent for Chat-based Inbox Interaction
Handles conversational queries about emails with RAG
"""
from typing import Dict, Any, List, Optional
from src.llm_client import LLMClient
from src.email_processor import EmailProcessor
from src.rag_system import EmailRAGSystem


class EmailAgent:
    """Conversational agent for interacting with email inbox using RAG"""
    
    def __init__(self, llm_client: LLMClient, email_processor: EmailProcessor):
        self.llm_client = llm_client
        self.email_processor = email_processor
        self.rag_system = EmailRAGSystem()
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
        
        # Use RAG to retrieve relevant emails
        relevant_emails = self.rag_system.retrieve_relevant_emails(user_query, top_k=10)
        
        # Build context with RAG results
        context = self._build_rag_context(user_query, selected_email, relevant_emails)
        
        # Create RAG-enhanced agent prompt
        prompt = f"""You are an intelligent Email Productivity Agent with RAG (Retrieval-Augmented Generation) capabilities.

CONTEXT PROVIDED:
The system has already retrieved the most relevant emails for this query using semantic search.
Use this pre-filtered context to provide accurate, specific answers.

{context}

User Query: {user_query}

INSTRUCTIONS:
- Use the RELEVANT EMAILS section above - these are the most important emails for this query
- Reference specific emails by their ID when answering
- Use the statistics to provide counts and summaries
- If asked about specific senders/subjects, look through the relevant emails
- Provide concrete, actionable responses based on actual email content
- If no relevant emails found, say so clearly
- Format your answer in PLAIN TEXT only - NO HTML tags, NO markdown formatting
- Use simple numbered lists (1. 2. 3.) or bullet points (•) for lists
- Write in clear, natural paragraphs with proper spacing

Respond in JSON format:
{{
  "answer": "<detailed response referencing specific emails from the context above>",
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
    
    def _build_rag_context(
        self,
        query: str,
        selected_email: Optional[Dict[str, Any]],
        relevant_emails: List[Dict[str, Any]]
    ) -> str:
        """Build RAG-enhanced context with relevant emails"""
        context_parts = []
        
        # Add email statistics
        stats = self.rag_system.get_stats()
        context_parts.append("=== EMAIL DATABASE STATISTICS ===")
        context_parts.append(f"Total Emails: {stats['total_emails']}")
        context_parts.append(f"Unread: {stats['unread']}")
        context_parts.append(f"Starred: {stats['starred']}")
        context_parts.append(f"Important: {stats['important']}")
        context_parts.append(f"Folders: {stats['folders']}")
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
            context_parts.append(f"    Preview: {email.get('body', '')[:100]}...")
            
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
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
