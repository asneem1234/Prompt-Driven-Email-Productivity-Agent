# 🎬 Demo Video Script - Prompt-Driven Email Productivity Agent
## Presenter: Asneem Athar Shaik | VIT-AP

**Total Duration**: 8-10 minutes  
**Recording Tips**: 
- Speak clearly and confidently
- Show your face in a small webcam window (optional but recommended)
- Use screen recording software (OBS Studio, Loom, or Windows Game Bar)
- Ensure audio quality is good
- Have the app running and ready before starting

---

## 🎯 INTRODUCTION (1 minute)

### Opening (15 seconds)
**[Face camera, then switch to screen]**

> "Hello! My name is Asneem Athar Shaik, and I'm a student at VIT-AP. Today, I'm excited to present my Prompt-Driven Email Productivity Agent - an intelligent system that transforms how we manage our inbox using AI and customizable prompts."

### Quick Overview (45 seconds)
**[Show browser with localhost:5000 ready to go]**

> "This is not just another email client. This is an AI-powered productivity agent that:
> - Automatically categorizes emails using color-coded tags
> - Extracts action items and deadlines
> - Generates intelligent draft replies
> - Provides a conversational chat interface powered by RAG technology
> - And most importantly - everything is driven by customizable prompts that YOU control
>
> The entire system is built with Flask on the backend, features a professional Gmail-style UI, and uses Google's Gemini 2.0 Flash model for AI capabilities. Let me show you how it works."

---

## 📧 SECTION 1: LOADING & VIEWING INBOX (1.5 minutes)

### Navigate to Application (20 seconds)
**[Type in browser: http://127.0.0.1:5000]**

> "Let's start by launching the application. I'm running this locally on port 5000."

**[App loads, redirects to inbox]**

> "As you can see, the application immediately loads our mock inbox. This is a professional Gmail-style interface that I've designed with Material Icons and Google's design language."

### Showcase Inbox Features (70 seconds)
**[Slowly scroll through email list]**

> "The inbox automatically loaded 25 sample emails from a JSON file. These aren't random - they're carefully crafted to represent real-world scenarios:
> - Meeting requests from colleagues
> - Project updates
> - Urgent notifications
> - Spam and promotional content
> - Task assignments with deadlines
>
> Notice the clean interface showing:
> - **Sender information** on the left
> - **Email subjects** prominently displayed
> - **Timestamps** showing when each email arrived
> - **Color-coded category badges** on the right
>
> Let me explain this color-coding system - it's a key feature:
> - 🔴 **RED badges** mean URGENT - requires immediate attention
> - 🟠 **ORANGE badges** mean DEADLINE - time-sensitive with specific dates
> - 🟢 **GREEN badges** mean CONVERSATION - informational, no urgent action
> - ⚫ **GREY badges** mean SPAM - promotional or low priority
> - And we have OTHER for anything that doesn't fit these categories"

**[Click on an email to show preview]**

> "When I click on any email, we can see the full content in a preview pane - sender details, subject line, timestamp, and the complete message body."

---

## 🧠 SECTION 2: THE PROMPT BRAIN - CUSTOMIZABLE PROMPTS (2 minutes)

### Navigate to Custom Prompt (15 seconds)
**[Click "Custom Prompt" in sidebar with psychology icon]**

> "Now, here's what makes this system truly unique - the Prompt Brain. This is where the magic happens. Click this psychology icon in the sidebar labeled 'Custom Prompt'."

### Overview of Prompt System (30 seconds)
**[Show the prompt selection dropdown]**

> "This is the control center of our AI agent. You can see we have four different types of prompts:
> 1. **Email Categorization** - determines how emails are classified
> 2. **Action Item Extraction** - identifies tasks and deadlines
> 3. **Auto-Reply Draft Generator** - creates intelligent responses
> 4. **Email Summarization** - generates concise summaries
>
> Each prompt is fully customizable. Let me show you what's inside."

### Demonstrate Categorization Prompt (40 seconds)
**[Select 'categorization' from dropdown, scroll through the prompt]**

> "This is the categorization prompt. Look at how detailed it is:
> - It defines exactly what each category means
> - It specifies color codes for visual feedback
> - It includes rules like 'Use Urgent for URGENT in subject, immediate action needed'
> - It tells the AI to respond in structured JSON format
>
> This prompt is injected into every categorization request. The AI uses these instructions to make consistent, intelligent decisions about email categories."

### Show Prompt Editing (35 seconds)
**[Click 'Edit Prompt' button, make a small change]**

> "Watch this - I can edit this prompt in real-time. Let me add a rule: 'Prioritize security alerts as Urgent'."

**[Type the change, click 'Save Prompt']**

> "When I save, the system immediately updates. Every future categorization will now follow this new rule. This is the power of prompt-driven architecture - you're not locked into pre-programmed behavior. You control how the AI thinks."

**[Optional: Click 'Test Prompt' to demonstrate]**

> "I can even test the prompt with sample data to see how it performs before using it on real emails."

---

## 🎨 SECTION 3: EMAIL CATEGORIZATION IN ACTION (2 minutes)

### Navigate Back to Inbox (10 seconds)
**[Click 'Inbox' in sidebar]**

> "Let me go back to the inbox and show you how these prompts work in action."

### Demonstrate "Categorize All" (90 seconds)
**[Point to 'Categorize All' button in toolbar]**

> "See this 'Categorize All' button? This is one of my favorite features. When I click it, the system processes every email in the inbox using our categorization prompt."

**[Click button, show the processing dialog]**

> "Watch the real-time feedback. The system is now:
> - Sending each email to Google's Gemini 2.0 Flash model
> - Using our custom prompt to analyze the content
> - Assigning appropriate color-coded categories
> - Handling rate limits intelligently with automatic delays"

**[Point to terminal/console if visible showing debug output]**

> "You can see in the console:
> - Each email being processed one by one
> - API calls being made
> - Categories being assigned
> - Success confirmations
>
> The system includes sophisticated error handling:
> - Automatic retries if the API times out
> - Rate limit detection and waiting
> - Quota exhaustion alerts
> - Graceful fallbacks for safety blocks"

**[Once processing completes]**

> "Perfect! All 25 emails are now categorized. Look at the variety:
> - This urgent server maintenance got a RED badge
> - This meeting request with a specific date got ORANGE
> - These casual team discussions got GREEN
> - And these promotional emails got GREY for spam"

**[Click on a few emails to show different categories]**

---

## 💬 SECTION 4: THE EMAIL AGENT CHAT (2.5 minutes)

### Navigate to Chat Interface (15 seconds)
**[Click 'Chat' in sidebar]**

> "Now let me show you the most powerful feature - the Email Agent. This is where our RAG system comes into play."

### Explain RAG System (30 seconds)
**[Show the chat interface]**

> "RAG stands for Retrieval-Augmented Generation. Here's what makes this special:
> - When you ask a question, the system doesn't just guess
> - It searches through your entire inbox using semantic similarity
> - It retrieves the 3 to 5 most relevant emails
> - It builds context from those emails
> - Then it uses the AI to generate an intelligent, context-aware answer
>
> Let me demonstrate with real queries."

### Demo Query 1: Finding Urgent Emails (30 seconds)
**[Type: "What are my urgent emails?"]**

> "First, let me ask: 'What are my urgent emails?'"

**[Hit send, show response]**

> "Look at this response! The agent:
> - Retrieved all emails marked as urgent
> - Listed them with clear formatting
> - Used the ⚠️ emoji to highlight urgency
> - Referenced specific email IDs like 'Email e007'
> - Provided sender information and key details
>
> This isn't a simple database query - the AI understood natural language and provided a contextual answer."

### Demo Query 2: Summarizing from Specific Sender (30 seconds)
**[Type: "Tell me about emails from Chris Lee"]**

> "Let's try something more complex: 'Tell me about emails from Chris Lee'"

**[Show response]**

> "Amazing! The agent:
> - Searched through all 25 emails
> - Found the ones from Chris Lee
> - Summarized the content
> - Extracted the key points
> - Identified any action items with the ✓ symbol
> - Even noted the deadline with 📅
>
> This demonstrates the semantic search capability - it understood I wanted information about a specific person."

### Demo Query 3: Task Extraction (30 seconds)
**[Type: "What tasks do I need to complete?"]**

> "Now let's ask: 'What tasks do I need to complete?'"

**[Show response]**

> "This is incredibly useful! The agent:
> - Scanned all emails using our action extraction prompt
> - Identified tasks that require my attention
> - Listed them with priorities
> - Provided deadlines where mentioned
> - Gave context about which email each task came from
>
> This is like having a personal assistant reading through your emails."

### Demo Query 4: Draft Generation (30 seconds)
**[Type: "Draft a reply to the meeting request"]**

> "Finally, let's generate a draft: 'Draft a reply to the meeting request'"

**[Show response]**

> "Perfect! The agent:
> - Identified which email was a meeting request
> - Used our auto-reply prompt template
> - Generated a professional response
> - Suggested specific time slots
> - Maintained appropriate tone
> - Didn't send it automatically - it's saved as a draft for my review
>
> This is the prompt-driven approach in action - the AI follows our reply guidelines exactly."

---

## 📝 SECTION 5: DRAFT MANAGEMENT (1 minute)

### Navigate to Drafts (15 seconds)
**[Click 'Drafts' in sidebar]**

> "Let me show you where those drafts are stored. Click on 'Drafts' in the sidebar."

### Show Draft Features (45 seconds)
**[Display drafts page with saved drafts]**

> "Here's our draft management system. You can see:
> - All AI-generated drafts saved here
> - Subject lines clearly visible
> - Timestamps showing when they were created
> - Preview of the draft content
>
> I can click on any draft to view the full text, edit it if needed, or delete it. The key safety feature here is that nothing is ever sent automatically. Every AI-generated response is saved as a draft first, giving you full control.

**[Click on a draft to show full content]**

> "This draft includes:
> - A professional subject line
> - Well-structured body text
> - Appropriate greeting and closing
> - All generated using our custom prompts
>
> If I wanted to send this, I would copy it to my actual email client. The system is designed for safety - it helps you write better emails, but never takes action without your explicit approval."

---

## 🎯 SECTION 6: TECHNICAL HIGHLIGHTS (1 minute)

### Architecture Overview (30 seconds)
**[Can show code editor briefly or just talk over the UI]**

> "Let me quickly highlight the technical architecture that makes this possible:
>
> **Backend Technology:**
> - Flask framework for the web server
> - Python for all business logic
> - Session-based state management for multi-user support
> - Modular component architecture
>
> **AI Integration:**
> - Google Gemini 2.0 Flash as our LLM
> - Custom retry logic for rate limit handling
> - Automatic error recovery
> - Structured prompt management system
>
> **Frontend Design:**
> - Gmail-inspired responsive UI
> - Material Icons for consistency
> - Real-time updates
> - Clean, professional aesthetics
>
> **Data Management:**
> - JSON-based storage for prompts
> - Mock inbox with 25 diverse emails
> - Draft storage system
> - Categorization state management"

### Unique Features (30 seconds)
**[Back to the UI, showing key screens]**

> "What makes this project stand out:
>
> 1. **True Prompt-Driven Architecture** - Not hardcoded AI behavior; everything is customizable through prompts
>
> 2. **RAG System** - Semantic search across your entire inbox for context-aware responses
>
> 3. **Color-Coded Categorization** - Visual system with 5 distinct categories
>
> 4. **Bulk Processing** - Categorize all emails at once with rate limit protection
>
> 5. **Safety First** - Draft-only approach, never auto-sends
>
> 6. **Professional UI** - Gmail-quality interface design
>
> 7. **Comprehensive Error Handling** - Graceful failures, automatic retries, quota management"

---

## 🏆 SECTION 7: CONCLUSION (45 seconds)

### Summary (30 seconds)
**[Show the inbox one final time]**

> "To summarize what we've seen today:
>
> This Prompt-Driven Email Productivity Agent successfully demonstrates:
> ✓ Automatic email categorization with color coding
> ✓ Customizable prompt system - the 'brain' of the agent
> ✓ Action item and deadline extraction
> ✓ Intelligent draft generation
> ✓ RAG-powered conversational interface
> ✓ Safe, draft-only email handling
> ✓ Professional, Gmail-inspired user experience
>
> Every requirement from the assignment has been met and exceeded. The system is functional, extensible, and ready for real-world use."

### Closing (15 seconds)
**[Face camera if possible]**

> "Thank you for watching this demonstration. This project showcases the power of prompt engineering, RAG systems, and thoughtful UI design. All source code is available on GitHub, with comprehensive documentation.
>
> I'm Asneem Athar Shaik from VIT-AP. Thank you!"

**[Fade out or end recording]**

---

## 📋 PRE-RECORDING CHECKLIST

Before you start recording, ensure:

### Application Setup
- [ ] Flask app is running on http://127.0.0.1:5000
- [ ] All 25 emails load successfully in inbox
- [ ] API key is configured in .env file
- [ ] No errors in terminal/console

### Browser Setup
- [ ] Close unnecessary tabs
- [ ] Clear browser history/cookies if needed
- [ ] Zoom level is at 100% for clear visibility
- [ ] Disable browser extensions that might interfere

### Screen Setup
- [ ] Close all unnecessary applications
- [ ] Disable notifications (Windows/Mac notification center)
- [ ] Set up clean desktop background
- [ ] Adjust screen resolution to 1920x1080 if possible

### Recording Software Setup
- [ ] Test audio levels (your voice should be clear)
- [ ] Test screen recording (ensure it captures entire screen)
- [ ] Practice opening/closing windows smoothly
- [ ] Have script readily available (second monitor or printed)

### Demo Flow Prep
- [ ] Test "Categorize All" button works
- [ ] Verify all prompts are visible in Custom Prompt page
- [ ] Check that chat responses are working
- [ ] Confirm drafts page displays correctly
- [ ] Prepare 3-4 test queries for the chat interface

### Practice Run
- [ ] Do a complete 2-minute dry run before recording
- [ ] Time each section to ensure it fits within limits
- [ ] Practice smooth transitions between sections
- [ ] Rehearse your introduction and conclusion

---

## 🎤 SPEAKING TIPS

### Voice & Delivery
1. **Speak clearly and at moderate pace** - Not too fast, not too slow
2. **Show enthusiasm** - This is YOUR project, be proud!
3. **Use natural pauses** - Give viewers time to absorb information
4. **Avoid filler words** - "um", "like", "you know" (practice helps)
5. **Smile when speaking** - It comes through in your voice

### Technical Presentation
1. **Move mouse slowly** - Quick movements are hard to follow
2. **Point with cursor** - Direct attention to specific UI elements
3. **Explain as you click** - Say what you're doing before doing it
4. **Read important text** - Don't assume viewers can read small text
5. **Zoom in if needed** - Make sure small details are visible

### Confidence Boosters
1. **Remember**: This is a demonstration, not a live presentation
2. **You can edit**: Cut out mistakes in post-production
3. **Take breaks**: Pause recording between sections if needed
4. **Redo sections**: Re-record any part you're not happy with
5. **Believe in your work**: You built something impressive!

---

## 🛠️ TROUBLESHOOTING DURING RECORDING

### If the app crashes:
> "Let me restart the application quickly..." [Restart, continue]

### If API gives an error:
> "We're experiencing a temporary API issue - let me show you the expected result..." [Show pre-categorized emails]

### If you forget something:
> "Before we move on, let me highlight one more important feature..." [Go back]

### If categorization takes too long:
> "The system is processing in real-time, working through each email with built-in rate limiting for API stability..." [Continue narration while waiting]

---

## 📊 POST-RECORDING CHECKLIST

After recording:
- [ ] Review entire video for audio/video quality
- [ ] Check that all features were demonstrated
- [ ] Verify timing (should be 8-10 minutes)
- [ ] Add title card: "Prompt-Driven Email Productivity Agent | Asneem Athar Shaik | VIT-AP"
- [ ] Add chapter markers (optional but nice):
  - 0:00 Introduction
  - 1:00 Inbox Loading
  - 2:30 Prompt Brain
  - 4:30 Email Categorization
  - 6:30 Chat Agent Demo
  - 8:30 Draft Management
  - 9:30 Conclusion

---

## 🎬 VIDEO EXPORT SETTINGS

Recommended settings:
- **Resolution**: 1920x1080 (Full HD)
- **Frame Rate**: 30fps
- **Format**: MP4 (H.264 codec)
- **Bitrate**: 8-10 Mbps
- **Audio**: AAC, 192kbps, 48kHz

---

## 💡 FINAL TIPS

1. **Energy is contagious** - Show your excitement about the project
2. **Tell a story** - You're showing a journey from inbox chaos to organized productivity
3. **Highlight your decisions** - Explain why you chose certain features
4. **Show personality** - This represents YOU, let it shine
5. **End strong** - The conclusion is what reviewers remember most

---

## 🎯 KEY PHRASES TO EMPHASIZE

Throughout the video, make sure to mention:

- ✅ "Prompt-driven architecture" - core concept
- ✅ "Customizable and extensible" - flexibility
- ✅ "RAG-powered" - technical sophistication  
- ✅ "Safety first with draft-only approach" - responsible AI
- ✅ "Gmail-inspired professional UI" - quality design
- ✅ "Real-world scenarios" - practical application
- ✅ "Fully functional and production-ready" - completeness

---

**Good luck, Asneem! You've built something impressive. Show it with confidence! 🚀**
