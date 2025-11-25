"""
Flask UI for Email Productivity Agent
Main application interface
"""
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from src.llm_client import LLMClient
from src.prompt_manager import PromptManager
from src.email_processor import EmailProcessor
from src.draft_manager import DraftManager
from src.email_agent import EmailAgent

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Global instances (will be initialized per session)
app_instances = {}



def get_or_create_instances():
    """Get or create application instances for the current session"""
    session_id = session.get('session_id')
    
    if not session_id:
        session_id = os.urandom(16).hex()
        session['session_id'] = session_id
    
    if session_id not in app_instances:
        api_key = os.environ.get('GEMINI_API_KEY', '')
        if api_key:
            app_instances[session_id] = {
                'llm_client': LLMClient(),
                'prompt_manager': PromptManager(),
                'initialized': True,
                'inbox': [],
                'processed_emails': {},
                'selected_email': None,
                'chat_history': []
            }
            
            # Initialize components
            instances = app_instances[session_id]
            instances['email_processor'] = EmailProcessor(
                instances['llm_client'],
                instances['prompt_manager']
            )
            instances['draft_manager'] = DraftManager(
                instances['llm_client'],
                instances['prompt_manager']
            )
            instances['email_agent'] = EmailAgent(
                instances['llm_client'],
                instances['email_processor']
            )
            
            # Auto-load inbox from mock data
            inbox_file = "data/mock_inbox.json"
            if os.path.exists(inbox_file):
                with open(inbox_file, 'r', encoding='utf-8') as f:
                    instances['inbox'] = json.load(f)
                
                # Index emails in RAG system immediately
                instances['email_agent'].rag_system.index_emails(instances['inbox'])
                print(f"🔍 RAG System initialized with {len(instances['inbox'])} emails")
        else:
            app_instances[session_id] = {
                'initialized': False,
                'inbox': [],
                'processed_emails': {},
                'selected_email': None,
                'chat_history': []
            }
    
    return app_instances[session_id]


@app.route('/')
def index():
    """Home page - redirect to inbox"""
    return redirect(url_for('inbox'))


@app.route('/setup', methods=['GET', 'POST'])
def setup():
    """Setup page for API key"""
    if request.method == 'POST':
        api_key = request.form.get('api_key')
        if api_key:
            os.environ['GEMINI_API_KEY'] = api_key
            # Reset session to reinitialize
            session_id = session.get('session_id')
            if session_id and session_id in app_instances:
                del app_instances[session_id]
            return redirect(url_for('index'))
    
    return render_template('setup.html')


@app.route('/inbox')
def inbox():
    """Inbox page"""
    instances = get_or_create_instances()
    
    # Get filter and sort parameters
    filter_category = request.args.get('category', 'All')
    sort_by = request.args.get('sort', 'date_newest')
    
    # Filter emails
    emails = instances['inbox']
    filtered_emails = []
    
    for email in emails:
        email_id = email['id']
        processed = instances['processed_emails'].get(email_id, {})
        
        # Apply category filter
        if filter_category != 'All':
            cat = processed.get('category', {}).get('category', 'Unknown')
            if cat != filter_category:
                continue
        
        # Attach processed data
        email['processed'] = processed
        filtered_emails.append(email)
    
    # Calculate stats
    stats = {
        'total': len(instances['inbox']),
        'processed': len(instances['processed_emails']),
        'categories': {}
    }
    
    for processed in instances['processed_emails'].values():
        if processed and isinstance(processed, dict):
            cat = processed.get('category', {}).get('category', 'Unknown')
            stats['categories'][cat] = stats['categories'].get(cat, 0) + 1
    
    return render_template('inbox.html', 
                         emails=filtered_emails, 
                         stats=stats,
                         filter_category=filter_category,
                         selected_email=instances.get('selected_email'))


@app.route('/api/load-inbox', methods=['POST'])
def load_inbox():
    """Load mock inbox from JSON file"""
    instances = get_or_create_instances()
    inbox_file = "data/mock_inbox.json"
    
    try:
        if os.path.exists(inbox_file):
            with open(inbox_file, 'r', encoding='utf-8') as f:
                instances['inbox'] = json.load(f)
            return jsonify({'success': True, 'count': len(instances['inbox'])})
        else:
            return jsonify({'success': False, 'error': 'Mock inbox file not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/process-all', methods=['POST'])
def process_all():
    """Process all emails in the inbox"""
    instances = get_or_create_instances()
    
    if not instances['inbox']:
        return jsonify({'success': False, 'error': 'No emails to process'})
    
    try:
        for email in instances['inbox']:
            result = instances['email_processor'].process_email(email)
            instances['processed_emails'][email['id']] = result
        
        return jsonify({'success': True, 'count': len(instances['inbox'])})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/process-email/<email_id>', methods=['POST'])
def process_email(email_id):
    """Process a single email"""
    instances = get_or_create_instances()
    
    # Find email
    email = next((e for e in instances['inbox'] if e['id'] == email_id), None)
    if not email:
        return jsonify({'success': False, 'error': 'Email not found'})
    
    try:
        result = instances['email_processor'].process_email(email)
        instances['processed_emails'][email_id] = result
        return jsonify({'success': True, 'result': result})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/select-email/<email_id>', methods=['POST'])
def select_email(email_id):
    """Select an email to view details"""
    instances = get_or_create_instances()
    
    email = next((e for e in instances['inbox'] if e['id'] == email_id), None)
    if email:
        instances['selected_email'] = email
        return jsonify({'success': True})
    
    return jsonify({'success': False, 'error': 'Email not found'})


@app.route('/api/deselect-email', methods=['POST'])
def deselect_email():
    """Deselect the currently selected email"""
    instances = get_or_create_instances()
    instances['selected_email'] = None
    return jsonify({'success': True})


@app.route('/prompt-brain')
def prompt_brain():
    """Prompt brain configuration page"""
    instances = get_or_create_instances()
    
    prompt_manager = instances['prompt_manager']
    all_prompts = prompt_manager.get_all_prompts()
    
    selected_type = request.args.get('type', list(all_prompts.keys())[0] if all_prompts else None)
    
    return render_template('prompt_brain.html', 
                         prompts=all_prompts,
                         selected_type=selected_type,
                         inbox=instances['inbox'][:5])


@app.route('/api/update-prompt', methods=['POST'])
def update_prompt():
    """Update a prompt"""
    instances = get_or_create_instances()
    
    data = request.json
    prompt_type = data.get('type')
    new_prompt = data.get('prompt')
    
    try:
        prompt_manager = instances['prompt_manager']
        all_prompts = prompt_manager.get_all_prompts()
        
        if prompt_type in all_prompts:
            prompt_data = all_prompts[prompt_type]
            prompt_data['prompt'] = new_prompt
            prompt_manager.update_prompt(prompt_type, prompt_data)
            return jsonify({'success': True})
        
        return jsonify({'success': False, 'error': 'Prompt type not found'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/test-prompt', methods=['POST'])
def test_prompt():
    """Test a prompt with an email"""
    instances = get_or_create_instances()
    
    data = request.json
    prompt_template = data.get('prompt')
    email_id = data.get('email_id')
    
    # Find email
    email = next((e for e in instances['inbox'] if e['id'] == email_id), None)
    if not email:
        return jsonify({'success': False, 'error': 'Email not found'})
    
    try:
        # Format prompt
        formatted_prompt = prompt_template.format(
            sender=email.get('sender', ''),
            subject=email.get('subject', ''),
            body=email.get('body', '')
        )
        
        # Call LLM
        result = instances['llm_client'].call_llm(formatted_prompt)
        
        return jsonify({
            'success': True,
            'formatted_prompt': formatted_prompt,
            'response': result
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/drafts')
def drafts():
    """Drafts page"""
    instances = get_or_create_instances()
    
    draft_manager = instances['draft_manager']
    all_drafts = draft_manager.get_all_drafts()
    
    # Sort by created_at
    all_drafts = sorted(all_drafts, key=lambda d: d.get('created_at', ''), reverse=True)
    
    return render_template('drafts.html', drafts=all_drafts)


@app.route('/api/generate-reply/<email_id>', methods=['POST'])
def generate_reply(email_id):
    """Generate a reply draft for an email"""
    instances = get_or_create_instances()
    
    email = next((e for e in instances['inbox'] if e['id'] == email_id), None)
    if not email:
        return jsonify({'success': False, 'error': 'Email not found'})
    
    try:
        result = instances['draft_manager'].generate_reply_draft(email)
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/generate-new-draft', methods=['POST'])
def generate_new_draft():
    """Generate a new email draft"""
    instances = get_or_create_instances()
    
    data = request.json
    recipient = data.get('recipient')
    subject = data.get('subject')
    context = data.get('context')
    tone = data.get('tone', 'professional')
    
    try:
        result = instances['draft_manager'].generate_new_email_draft(
            recipient, subject, context, tone
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/delete-draft/<draft_id>', methods=['DELETE'])
def delete_draft(draft_id):
    """Delete a draft"""
    instances = get_or_create_instances()
    
    try:
        instances['draft_manager'].delete_draft(draft_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/export-draft/<draft_id>')
def export_draft(draft_id):
    """Export a draft as text"""
    instances = get_or_create_instances()
    
    try:
        export_text = instances['draft_manager'].export_draft_as_text(draft_id)
        return export_text, 200, {
            'Content-Type': 'text/plain',
            'Content-Disposition': f'attachment; filename=draft_{draft_id}.txt'
        }
    except Exception as e:
        return str(e), 404


@app.route('/chat')
def chat():
    """Email agent chat page"""
    instances = get_or_create_instances()
    
    return render_template('chat.html', chat_history=instances['chat_history'])


def format_response(text: str) -> str:
    """Format and clean LLM response for display"""
    if not text:
        return text
    
    # Remove markdown formatting
    text = text.replace('**', '')
    text = text.replace('* *', '')
    text = text.replace('##', '')
    
    # Clean up extra spaces
    import re
    text = re.sub(r'\s+', ' ', text)
    
    # Format lists properly
    text = text.replace('* ', '\n• ')
    
    return text.strip()


@app.route('/api/chat', methods=['POST'])
def chat_query():
    """Handle chat query"""
    instances = get_or_create_instances()
    
    data = request.json
    query = data.get('query')
    
    if not query:
        return jsonify({'success': False, 'error': 'No query provided'})
    
    try:
        result = instances['email_agent'].query(
            query,
            selected_email=instances.get('selected_email'),
            context_emails=instances['inbox']
        )
        
        if result['success']:
            # Format the response
            answer = result['response'].get('answer', 'Sorry, I could not process that request.')
            formatted_answer = format_response(answer)
            
            # Add to chat history
            instances['chat_history'].append({'role': 'user', 'content': query})
            instances['chat_history'].append({
                'role': 'assistant', 
                'content': formatted_answer
            })
            
            # Update result with formatted answer
            result['response']['answer'] = formatted_answer
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


@app.route('/api/clear-chat', methods=['POST'])
def clear_chat():
    """Clear chat history"""
    instances = get_or_create_instances()
    instances['chat_history'] = []
    return jsonify({'success': True})


# For Vercel serverless deployment
application = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
