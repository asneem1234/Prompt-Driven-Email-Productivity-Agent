"""
Streamlit UI for Email Productivity Agent
Main application interface
"""
import streamlit as st
import json
import os
from datetime import datetime
from src.llm_client import LLMClient
from src.prompt_manager import PromptManager
from src.email_processor import EmailProcessor
from src.draft_manager import DraftManager
from src.email_agent import EmailAgent


# Page configuration
st.set_page_config(
    page_title="Email Productivity Agent",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .email-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f9f9f9;
    }
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    .important { background-color: #ff4444; color: white; }
    .newsletter { background-color: #4444ff; color: white; }
    .spam { background-color: #888888; color: white; }
    .to-do { background-color: #ff8800; color: white; }
    .meeting { background-color: #00aa00; color: white; }
    .draft-card {
        border-left: 4px solid #1f77b4;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: #f0f8ff;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.llm_client = None
        st.session_state.prompt_manager = None
        st.session_state.email_processor = None
        st.session_state.draft_manager = None
        st.session_state.email_agent = None
        st.session_state.inbox = []
        st.session_state.processed_emails = {}
        st.session_state.selected_email = None
        st.session_state.chat_history = []
        st.session_state.api_key = ""


def initialize_app():
    """Initialize the application with API key"""
    try:
        # Set environment variable
        os.environ['GEMINI_API_KEY'] = st.session_state.api_key
        
        # Initialize components
        st.session_state.llm_client = LLMClient()
        st.session_state.prompt_manager = PromptManager()
        st.session_state.email_processor = EmailProcessor(
            st.session_state.llm_client,
            st.session_state.prompt_manager
        )
        st.session_state.draft_manager = DraftManager(
            st.session_state.llm_client,
            st.session_state.prompt_manager
        )
        st.session_state.email_agent = EmailAgent(
            st.session_state.llm_client,
            st.session_state.email_processor
        )
        
        st.session_state.initialized = True
        st.success("✅ Application initialized successfully!")
        
    except Exception as e:
        st.error(f"❌ Initialization failed: {str(e)}")
        st.session_state.initialized = False


def load_mock_inbox():
    """Load mock inbox from JSON file"""
    inbox_file = "data/mock_inbox.json"
    if os.path.exists(inbox_file):
        with open(inbox_file, 'r', encoding='utf-8') as f:
            st.session_state.inbox = json.load(f)
        st.success(f"✅ Loaded {len(st.session_state.inbox)} emails from mock inbox")
    else:
        st.error(f"❌ Mock inbox file not found: {inbox_file}")


def process_inbox():
    """Process all emails in the inbox"""
    if not st.session_state.inbox:
        st.warning("⚠️ No emails to process. Load inbox first.")
        return
    
    with st.spinner("Processing emails... This may take a minute."):
        progress_bar = st.progress(0)
        
        for idx, email in enumerate(st.session_state.inbox):
            result = st.session_state.email_processor.process_email(email)
            st.session_state.processed_emails[email['id']] = result
            progress_bar.progress((idx + 1) / len(st.session_state.inbox))
        
        st.success(f"✅ Processed {len(st.session_state.inbox)} emails!")


def render_sidebar():
    """Render sidebar with navigation and controls"""
    with st.sidebar:
        st.markdown("### 📧 Email Productivity Agent")
        st.markdown("---")
        
        # API Key input
        if not st.session_state.initialized:
            st.markdown("#### 🔑 Setup")
            api_key = st.text_input(
                "Google Gemini API Key",
                type="password",
                value=st.session_state.api_key,
                help="Get free API key from: https://makersuite.google.com/app/apikey"
            )
            st.session_state.api_key = api_key
            
            if st.button("Initialize Application", type="primary"):
                if api_key:
                    initialize_app()
                else:
                    st.error("Please enter an API key")
        
        # Navigation
        if st.session_state.initialized:
            st.markdown("#### 📑 Navigation")
            page = st.radio(
                "Go to",
                ["📥 Inbox", "🧠 Prompt Brain", "✉️ Drafts", "💬 Email Agent Chat"],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            
            # Inbox controls
            st.markdown("#### ⚙️ Controls")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📂 Load Inbox", use_container_width=True):
                    load_mock_inbox()
            
            with col2:
                if st.button("⚡ Process All", use_container_width=True):
                    process_inbox()
            
            # Stats
            if st.session_state.processed_emails:
                st.markdown("---")
                st.markdown("#### 📊 Stats")
                
                categories = {}
                for email_id, processed in st.session_state.processed_emails.items():
                    if processed and isinstance(processed, dict):
                        cat = processed.get('category', {}).get('category', 'Unknown') if isinstance(processed.get('category'), dict) else 'Unknown'
                        categories[cat] = categories.get(cat, 0) + 1
                
                st.metric("Total Emails", len(st.session_state.inbox))
                st.metric("Processed", len(st.session_state.processed_emails))
                
                for cat, count in categories.items():
                    st.markdown(f"**{cat}:** {count}")
            
            return page
    
    return None


def render_inbox_page():
    """Render the inbox page"""
    st.markdown('<div class="main-header">📥 Email Inbox</div>', unsafe_allow_html=True)
    
    if not st.session_state.inbox:
        st.info("👆 Click 'Load Inbox' in the sidebar to get started")
        return
    
    # Filter controls
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        filter_category = st.selectbox(
            "Filter by Category",
            ["All", "Important", "Newsletter", "Spam", "To-Do", "Meeting"]
        )
    
    with col2:
        sort_by = st.selectbox(
            "Sort by",
            ["Date (Newest)", "Date (Oldest)", "Sender"]
        )
    
    # Display emails
    for email in st.session_state.inbox:
        email_id = email['id']
        processed = st.session_state.processed_emails.get(email_id)
        
        # Apply filter
        if filter_category != "All" and processed:
            cat = processed.get('category', {}).get('category', 'Unknown')
            if cat != filter_category:
                continue
        
        # Email card
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                # Category badge
                if processed and processed.get('category'):
                    cat = processed['category'].get('category', 'Unknown')
                    cat_class = cat.lower().replace('-', '')
                    st.markdown(
                        f'<span class="category-badge {cat_class}">{cat}</span>',
                        unsafe_allow_html=True
                    )
                
                st.markdown(f"**From:** {email.get('sender_name', email.get('sender'))}")
                st.markdown(f"**Subject:** {email.get('subject')}")
                
                # Show summary if processed
                if processed and processed.get('summary'):
                    with st.expander("📝 Summary & Actions"):
                        summary = processed['summary']
                        st.write(summary.get('summary', ''))
                        
                        if summary.get('key_points'):
                            st.markdown("**Key Points:**")
                            for point in summary['key_points']:
                                st.markdown(f"- {point}")
                        
                        # Action items
                        if processed.get('action_items'):
                            st.markdown("**Action Items:**")
                            for action in processed['action_items']:
                                deadline = action.get('deadline', 'none')
                                priority = action.get('priority', 'medium')
                                st.markdown(f"- [{priority.upper()}] {action['task']} (Due: {deadline})")
            
            with col2:
                if st.button("👁️ View", key=f"view_{email_id}"):
                    st.session_state.selected_email = email
                    st.rerun()
    
    # Selected email detail
    if st.session_state.selected_email:
        st.markdown("---")
        st.markdown("### 📧 Email Details")
        
        email = st.session_state.selected_email
        processed = st.session_state.processed_emails.get(email['id'])
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**From:** {email.get('sender_name', email.get('sender'))}")
            st.markdown(f"**Subject:** {email.get('subject')}")
            st.markdown(f"**Date:** {email.get('timestamp')}")
            
            st.markdown("**Body:**")
            st.text_area("", email.get('body', ''), height=200, disabled=True, label_visibility="collapsed")
        
        with col2:
            if st.button("✍️ Draft Reply", use_container_width=True):
                with st.spinner("Generating draft..."):
                    result = st.session_state.draft_manager.generate_reply_draft(email)
                    if result['success']:
                        st.success("✅ Draft created!")
                    else:
                        st.error(f"❌ Error: {result['error']}")
            
            if st.button("🔄 Re-process", use_container_width=True):
                with st.spinner("Processing..."):
                    result = st.session_state.email_processor.process_email(email)
                    st.session_state.processed_emails[email['id']] = result
                    st.success("✅ Email re-processed!")
                    st.rerun()


def render_prompt_brain_page():
    """Render the prompt brain configuration page"""
    st.markdown('<div class="main-header">🧠 Prompt Brain</div>', unsafe_allow_html=True)
    st.markdown("Configure the prompts that control the agent's behavior")
    
    prompt_manager = st.session_state.prompt_manager
    all_prompts = prompt_manager.get_all_prompts()
    
    # Prompt selector
    prompt_type = st.selectbox(
        "Select Prompt to Edit",
        list(all_prompts.keys())
    )
    
    if prompt_type:
        prompt_data = all_prompts[prompt_type]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"### {prompt_data.get('name', prompt_type)}")
            st.markdown(f"*{prompt_data.get('description', '')}*")
            
            # Edit prompt
            new_prompt = st.text_area(
                "Prompt Template",
                prompt_data.get('prompt', ''),
                height=300,
                help="Use {sender}, {subject}, {body} as placeholders"
            )
            
            # Test prompt
            st.markdown("#### 🧪 Test Prompt")
            
            if st.session_state.inbox:
                test_email_options = [f"{e['id']}: {e['subject'][:50]}..." for e in st.session_state.inbox[:5]]
                selected_test = st.selectbox("Select test email", test_email_options)
                
                if st.button("🚀 Test Prompt"):
                    # Get selected email
                    test_email_id = selected_test.split(":")[0]
                    test_email = next(e for e in st.session_state.inbox if e['id'] == test_email_id)
                    
                    # Format and display
                    formatted_prompt = new_prompt.format(
                        sender=test_email.get('sender', ''),
                        subject=test_email.get('subject', ''),
                        body=test_email.get('body', '')
                    )
                    
                    st.markdown("**Formatted Prompt:**")
                    st.code(formatted_prompt, language="text")
                    
                    # Call LLM
                    with st.spinner("Calling LLM..."):
                        result = st.session_state.llm_client.call_llm(formatted_prompt)
                        
                        st.markdown("**LLM Response:**")
                        if result['success']:
                            st.json(result['response'])
                        else:
                            st.error(f"Error: {result['error']}")
        
        with col2:
            st.markdown("### Actions")
            
            if st.button("💾 Save Prompt", type="primary", use_container_width=True):
                prompt_data['prompt'] = new_prompt
                prompt_manager.update_prompt(prompt_type, prompt_data)
                st.success("✅ Prompt saved!")
            
            if st.button("🔄 Reset to Default", use_container_width=True):
                # Reload from file
                prompt_manager.load_prompts()
                st.success("✅ Prompt reset!")
                st.rerun()
            
            # Prompt history
            st.markdown("---")
            st.markdown("### 📜 Version History")
            history = prompt_manager.get_prompt_history()
            st.metric("Versions", len(history))


def render_drafts_page():
    """Render the drafts page"""
    st.markdown('<div class="main-header">✉️ Email Drafts</div>', unsafe_allow_html=True)
    st.markdown("**⚠️ All drafts are saved locally and never sent automatically**")
    
    # Tabs for different draft types
    tab1, tab2 = st.tabs(["📝 Saved Drafts", "➕ New Draft"])
    
    with tab1:
        drafts = st.session_state.draft_manager.get_all_drafts()
        
        if not drafts:
            st.info("No drafts yet. Reply to an email or create a new draft to get started.")
        else:
            for draft in sorted(drafts, key=lambda d: d.get('created_at', ''), reverse=True):
                with st.container():
                    st.markdown('<div class="draft-card">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        content = draft.get('draft_content', {})
                        st.markdown(f"**Subject:** {content.get('subject', 'No Subject')}")
                        
                        if draft.get('in_reply_to'):
                            reply_to = draft['in_reply_to']
                            st.markdown(f"*In reply to: {reply_to.get('subject')} (from {reply_to.get('sender')})*")
                        
                        st.markdown(f"**Created:** {draft.get('created_at', '')[:19]}")
                        
                        with st.expander("📄 View Draft"):
                            st.markdown("**Body:**")
                            st.write(content.get('body', ''))
                            
                            if content.get('suggested_actions'):
                                st.markdown("**Suggested Follow-ups:**")
                                for action in content['suggested_actions']:
                                    st.markdown(f"- {action}")
                    
                    with col2:
                        if st.button("📤 Export", key=f"export_{draft['id']}", use_container_width=True):
                            export_text = st.session_state.draft_manager.export_draft_as_text(draft['id'])
                            st.download_button(
                                "⬇️ Download",
                                export_text,
                                file_name=f"draft_{draft['id']}.txt",
                                key=f"download_{draft['id']}"
                            )
                        
                        if st.button("🗑️ Delete", key=f"delete_{draft['id']}", use_container_width=True):
                            st.session_state.draft_manager.delete_draft(draft['id'])
                            st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### Create New Email Draft")
        
        recipient = st.text_input("To:", placeholder="recipient@example.com")
        subject = st.text_input("Subject:", placeholder="Email subject")
        context = st.text_area(
            "Context/Instructions:",
            placeholder="Describe what the email should be about...",
            height=150
        )
        tone = st.selectbox("Tone:", ["professional", "friendly", "formal"])
        
        if st.button("✨ Generate Draft", type="primary"):
            if recipient and subject and context:
                with st.spinner("Generating draft..."):
                    result = st.session_state.draft_manager.generate_new_email_draft(
                        recipient, subject, context, tone
                    )
                    
                    if result['success']:
                        st.success("✅ Draft created!")
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result['error']}")
            else:
                st.warning("Please fill in all fields")


def render_chat_page():
    """Render the email agent chat page"""
    st.markdown('<div class="main-header">💬 Email Agent Chat</div>', unsafe_allow_html=True)
    st.markdown("Ask questions about your inbox, get summaries, or request actions")
    
    # Chat history
    if 'chat_messages' not in st.session_state:
        st.session_state.chat_messages = []
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask about your emails..."):
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.email_agent.query(
                    prompt,
                    selected_email=st.session_state.selected_email,
                    context_emails=st.session_state.inbox
                )
                
                if result['success']:
                    response = result['response']
                    answer = response.get('answer', 'Sorry, I could not process that request.')
                    
                    st.markdown(answer)
                    
                    # Show suggested actions if any
                    if response.get('suggested_actions'):
                        st.markdown("**Suggested Actions:**")
                        for action in response['suggested_actions']:
                            st.markdown(f"- {action}")
                    
                    # Add to chat history
                    st.session_state.chat_messages.append({"role": "assistant", "content": answer})
                else:
                    error_msg = f"❌ Error: {result.get('error', 'Unknown error')}"
                    st.error(error_msg)
                    st.session_state.chat_messages.append({"role": "assistant", "content": error_msg})
    
    # Quick actions
    st.markdown("---")
    st.markdown("**💡 Quick Actions:**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📋 Show all tasks"):
            st.session_state.chat_messages.append({
                "role": "user",
                "content": "What tasks do I need to do?"
            })
            st.rerun()
    
    with col2:
        if st.button("⚡ Show urgent emails"):
            st.session_state.chat_messages.append({
                "role": "user",
                "content": "Show me all urgent or important emails"
            })
            st.rerun()
    
    with col3:
        if st.button("📊 Inbox summary"):
            st.session_state.chat_messages.append({
                "role": "user",
                "content": "Give me a summary of my inbox"
            })
            st.rerun()


def main():
    """Main application entry point"""
    initialize_session_state()
    
    # Render sidebar and get selected page
    page = render_sidebar()
    
    # Render selected page
    if not st.session_state.initialized:
        st.markdown('<div class="main-header">📧 Email Productivity Agent</div>', unsafe_allow_html=True)
        st.info("👈 Please enter your OpenAI API key in the sidebar to get started")
        
        st.markdown("### 🎯 Features")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            - 📥 **Inbox Management**: Load and process emails
            - 🏷️ **Auto-Categorization**: Intelligent email sorting
            - ✅ **Action Extraction**: Automatic task identification
            - 📝 **Smart Summaries**: Quick email overviews
            """)
        
        with col2:
            st.markdown("""
            - 🧠 **Prompt Brain**: Customize agent behavior
            - ✉️ **Draft Generation**: AI-powered email replies
            - 💬 **Email Agent Chat**: Natural language inbox queries
            - 🔒 **Safety First**: Drafts only, never sends
            """)
    
    elif page == "📥 Inbox":
        render_inbox_page()
    elif page == "🧠 Prompt Brain":
        render_prompt_brain_page()
    elif page == "✉️ Drafts":
        render_drafts_page()
    elif page == "💬 Email Agent Chat":
        render_chat_page()


if __name__ == "__main__":
    main()
