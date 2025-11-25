"""
RAG (Retrieval-Augmented Generation) System for Email Agent
Uses semantic search to find relevant emails for user queries
"""
import numpy as np
from typing import Dict, Any, List, Tuple
import json
import re


class EmailRAGSystem:
    """RAG system with semantic search for emails"""
    
    def __init__(self):
        self.emails = []
        self.email_embeddings = {}
        self.indexed = False
    
    def index_emails(self, emails: List[Dict[str, Any]]):
        """
        Index emails for RAG retrieval
        Creates searchable representations of each email
        """
        self.emails = emails
        self.email_embeddings = {}
        
        for email in emails:
            email_id = email.get('id')
            
            # Create rich text representation for embedding
            email_text = self._create_email_text(email)
            
            # Create simple keyword-based embedding (lightweight approach)
            embedding = self._create_embedding(email_text)
            
            self.email_embeddings[email_id] = {
                'text': email_text,
                'embedding': embedding,
                'email': email
            }
        
        self.indexed = True
        print(f"✅ RAG System indexed {len(emails)} emails")
    
    def _create_email_text(self, email: Dict[str, Any]) -> str:
        """Create searchable text representation of email"""
        parts = []
        
        # Add all searchable fields
        parts.append(f"From: {email.get('sender_name', '')} {email.get('sender', '')}")
        parts.append(f"Subject: {email.get('subject', '')}")
        parts.append(f"Body: {email.get('body', '')}")
        parts.append(f"Date: {email.get('timestamp', '')}")
        
        # Add flags
        if email.get('starred'):
            parts.append("STARRED IMPORTANT")
        if email.get('important'):
            parts.append("IMPORTANT PRIORITY")
        if email.get('read') == False:
            parts.append("UNREAD NEW")
        
        # Add folder
        folder = email.get('folder', 'inbox')
        parts.append(f"Folder: {folder}")
        
        return " ".join(parts).lower()
    
    def _create_embedding(self, text: str) -> Dict[str, float]:
        """
        Create a simple keyword-based embedding
        This is lightweight and doesn't require external models
        """
        # Extract keywords and their frequencies
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Create frequency-based embedding
        embedding = {}
        for word in words:
            if len(word) > 2:  # Skip very short words
                embedding[word] = embedding.get(word, 0) + 1
        
        return embedding
    
    def retrieve_relevant_emails(
        self, 
        query: str, 
        top_k: int = 10,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve most relevant emails for a query using semantic search
        
        Args:
            query: User's search query
            top_k: Number of emails to return
            filters: Optional filters (sender, starred, unread, etc.)
            
        Returns:
            List of relevant emails with relevance scores
        """
        if not self.indexed:
            return []
        
        # Create query embedding
        query_embedding = self._create_embedding(query.lower())
        
        # Calculate similarity scores for all emails
        scores = []
        for email_id, data in self.email_embeddings.items():
            # Calculate similarity
            score = self._calculate_similarity(query_embedding, data['embedding'])
            
            # Apply keyword boost
            if self._has_keywords(query.lower(), data['text']):
                score *= 1.5
            
            # Apply filters
            if filters:
                if not self._matches_filters(data['email'], filters):
                    continue
            
            scores.append({
                'email': data['email'],
                'score': score,
                'email_id': email_id
            })
        
        # Sort by relevance score
        scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Return top_k results
        return scores[:top_k]
    
    def _calculate_similarity(
        self, 
        query_emb: Dict[str, float], 
        doc_emb: Dict[str, float]
    ) -> float:
        """Calculate cosine similarity between query and document"""
        if not query_emb or not doc_emb:
            return 0.0
        
        # Calculate dot product
        dot_product = 0
        for word, freq in query_emb.items():
            if word in doc_emb:
                dot_product += freq * doc_emb[word]
        
        # Calculate magnitudes
        query_mag = sum(f * f for f in query_emb.values()) ** 0.5
        doc_mag = sum(f * f for f in doc_emb.values()) ** 0.5
        
        if query_mag == 0 or doc_mag == 0:
            return 0.0
        
        return dot_product / (query_mag * doc_mag)
    
    def _has_keywords(self, query: str, text: str) -> bool:
        """Check if text contains query keywords"""
        query_words = set(re.findall(r'\b\w+\b', query.lower()))
        
        # Check for exact phrase match
        if query in text:
            return True
        
        # Check for keyword matches
        matches = sum(1 for word in query_words if word in text)
        return matches >= max(1, len(query_words) * 0.5)
    
    def _matches_filters(self, email: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if email matches given filters"""
        if filters.get('sender'):
            if filters['sender'].lower() not in email.get('sender', '').lower():
                return False
        
        if filters.get('starred') is not None:
            if email.get('starred') != filters['starred']:
                return False
        
        if filters.get('unread') is not None:
            if email.get('read') == filters['unread']:  # Note: read is opposite of unread
                return False
        
        if filters.get('important') is not None:
            if email.get('important') != filters['important']:
                return False
        
        if filters.get('folder'):
            if email.get('folder') != filters['folder']:
                return False
        
        return True
    
    def search_by_sender(self, sender: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """Search emails by sender"""
        return self.retrieve_relevant_emails(
            query=f"from {sender}",
            top_k=top_k,
            filters={'sender': sender}
        )
    
    def search_by_keywords(self, keywords: List[str], top_k: int = 10) -> List[Dict[str, Any]]:
        """Search emails by keywords"""
        query = " ".join(keywords)
        return self.retrieve_relevant_emails(query=query, top_k=top_k)
    
    def get_unread_emails(self) -> List[Dict[str, Any]]:
        """Get all unread emails"""
        return [email for email in self.emails if email.get('read') == False]
    
    def get_starred_emails(self) -> List[Dict[str, Any]]:
        """Get all starred emails"""
        return [email for email in self.emails if email.get('starred') == True]
    
    def get_important_emails(self) -> List[Dict[str, Any]]:
        """Get all important emails"""
        return [email for email in self.emails if email.get('important') == True]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get email statistics"""
        total = len(self.emails)
        unread = len(self.get_unread_emails())
        starred = len(self.get_starred_emails())
        important = len(self.get_important_emails())
        
        # Count by sender
        senders = {}
        for email in self.emails:
            sender = email.get('sender_name', email.get('sender', 'Unknown'))
            senders[sender] = senders.get(sender, 0) + 1
        
        # Count by folder
        folders = {}
        for email in self.emails:
            folder = email.get('folder', 'inbox')
            folders[folder] = folders.get(folder, 0) + 1
        
        return {
            'total_emails': total,
            'unread': unread,
            'starred': starred,
            'important': important,
            'top_senders': sorted(senders.items(), key=lambda x: x[1], reverse=True)[:5],
            'folders': folders
        }
