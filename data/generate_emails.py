import json
import random
from datetime import datetime, timedelta

# Email templates
subjects = [
    "Project Update - Week 47",
    "Meeting Invitation: Q1 Planning",
    "URGENT: Server Maintenance Tonight",
    "Re: Budget Approval Request",
    "Invoice #12345 from Vendor",
    "Your Weekly Newsletter",
    "Team Lunch This Friday?",
    "Code Review Request - PR #456",
    "Customer Feedback - Action Required",
    "Welcome to Our Service!",
    "Password Reset Confirmation",
    "Monthly Report Summary",
    "Re: Partnership Proposal",
    "Training Session Reminder",
    "System Update Notification",
    "Happy Birthday!",
    "Conference Registration Confirmed",
    "Important Security Update",
    "Re: Contract Renewal Discussion",
    "Holiday Schedule 2025",
]

senders = [
    ("alice.johnson@techcorp.com", "Alice Johnson"),
    ("bob.martinez@company.com", "Bob Martinez"),
    ("sarah.chen@partner.org", "Sarah Chen"),
    ("david.kim@startup.io", "David Kim"),
    ("emma.wilson@consulting.com", "Emma Wilson"),
    ("john.doe@enterprise.net", "John Doe"),
    ("lisa.brown@agency.co", "Lisa Brown"),
    ("michael.garcia@firm.com", "Michael Garcia"),
    ("anna.patel@tech.org", "Anna Patel"),
    ("chris.lee@solutions.com", "Chris Lee"),
    ("newsletter@techdigest.com", "Tech Digest"),
    ("notifications@linkedin.com", "LinkedIn"),
    ("noreply@github.com", "GitHub"),
    ("support@service.com", "Support Team"),
    ("hr@company.com", "HR Department"),
]

bodies = [
    "Hi,\n\nJust wanted to follow up on our previous discussion. Please let me know your thoughts.\n\nBest regards",
    "Hello,\n\nAttached is the document we discussed. Please review and provide feedback by EOD.\n\nThanks",
    "Hi there,\n\nThis is a friendly reminder about the upcoming deadline. Please prioritize this task.\n\nRegards",
    "Good morning,\n\nI hope this email finds you well. I wanted to discuss the next steps for our project.\n\nBest",
    "Dear team,\n\nPlease find the latest updates below. Let me know if you have any questions.\n\nCheers",
]

emails = []
now = datetime.now()

for i in range(1, 101):
    sender_email, sender_name = random.choice(senders)
    subject = random.choice(subjects)
    body = random.choice(bodies)
    days_ago = random.randint(0, 30)
    timestamp = (now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))).isoformat() + "Z"
    
    email = {
        "id": f"e{i:03d}",
        "sender": sender_email,
        "sender_name": sender_name,
        "subject": subject,
        "timestamp": timestamp,
        "body": body,
        "thread_id": f"thread_{i:03d}",
        "read": i > 44,  # First 44 are unread
        "starred": i in [3, 7, 12, 18, 25, 31, 39, 45, 52, 61, 73, 88],  # 12 starred emails
        "important": i in [4, 15, 22, 33, 41, 56, 67, 78, 89, 95],  # 10 important
        "folder": "sent" if i in range(85, 95) else ("drafts" if i in range(95, 101) else "inbox")
    }
    emails.append(email)

# Save to file
with open('data/mock_inbox.json', 'w') as f:
    json.dump(emails, f, indent=2)

print(f"✅ Generated {len(emails)} emails")
print(f"📬 Unread: {sum(1 for e in emails if not e['read'])}")
print(f"⭐ Starred: {sum(1 for e in emails if e['starred'])}")
print(f"📤 Sent: {sum(1 for e in emails if e['folder'] == 'sent')}")
print(f"📝 Drafts: {sum(1 for e in emails if e['folder'] == 'drafts')}")
