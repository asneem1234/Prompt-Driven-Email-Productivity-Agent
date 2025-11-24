# 🔑 Getting Your FREE Google Gemini API Key

The Email Productivity Agent uses **Google Gemini AI**, which is **FREE** with generous limits!

## Step-by-Step Guide

### 1. Visit Google AI Studio
Go to: **https://makersuite.google.com/app/apikey**

Or search for "Google AI Studio API Key"

### 2. Sign in with Google Account
- Use any Google account (Gmail, etc.)
- No payment method required!

### 3. Create API Key
1. Click **"Create API Key"** button
2. Select existing project or create new one
3. Copy the API key (starts with `AIza...`)

### 4. Use in the Application

**Option A: Enter in UI** (Recommended)
1. Run `streamlit run app.py`
2. Paste API key in sidebar
3. Click "Initialize Application"

**Option B: Environment File**
1. Copy `.env.example` to `.env`
2. Add: `GEMINI_API_KEY=your_key_here`
3. Run the app

## ✅ API Key Features

- **FREE** - No credit card required
- **Generous Limits** - 60 requests per minute
- **Fast** - Gemini 1.5 Flash is lightning quick
- **Smart** - Comparable to GPT-3.5/4

## 🔒 Security

- Keep your API key private
- Don't commit it to GitHub
- Don't share it publicly
- Regenerate if compromised

## 💡 Model Options

The app uses `gemini-1.5-flash` by default (fast & free). You can also use:
- `gemini-1.5-pro` - Smarter, slightly slower
- `gemini-pro` - Previous generation

Edit `src/llm_client.py` line 19 to change models.

## 📊 Rate Limits (Free Tier)

- **Requests per minute**: 60
- **Requests per day**: 1,500
- **Tokens per minute**: 1 million

Perfect for this demo! 🚀

## ❓ Troubleshooting

**Problem**: "API key not found"
- **Solution**: Make sure you copied the full key (starts with AIza)

**Problem**: "API quota exceeded"
- **Solution**: Wait a minute and try again (60 requests/min limit)

**Problem**: "Invalid API key"
- **Solution**: Generate a new key from the link above

## 🎯 Why Gemini?

1. **FREE** - No cost barriers
2. **Fast** - Quick response times
3. **Easy** - Simple to get started
4. **Powerful** - Great for email processing
5. **Reliable** - Google infrastructure

---

**Ready to get started?** 

👉 Get your key: https://makersuite.google.com/app/apikey

Then run: `streamlit run app.py`
