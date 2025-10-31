# 🚀 Nexus Assistant - Complete Setup Guide

## ✅ What's Already Done

All 38 Georgian law files have been analyzed and updated with **ACCURATE** English metadata:
- ✅ `laws/` directory contains 38 .txt files
- ✅ Each file has correct Georgian law name (first line)
- ✅ Each file has English SUMMARY_EN and KEYWORDS_EN
- ✅ Flask application fully built
- ✅ All templates created
- ✅ CSS and JavaScript ready

## 📋 Quick Setup (5 Minutes)

### Step 1: Install Python Dependencies

Open terminal in this folder and run:

```bash
pip install -r requirements.txt
```

**What gets installed:**
- Flask 3.0.0 (web framework)
- google-generativeai 0.3.2 (Gemini AI)
- python-dotenv 1.0.0 (environment variables)
- Werkzeug 3.0.1 (Flask utilities)

### Step 2: Get Your FREE Gemini API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key (looks like: `AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX`)

### Step 3: Configure Environment

Create `.env` file from template:

```bash
cp .env.template .env
```

Or on Windows:
```bash
copy .env.template .env
```

Edit `.env` and add your API key:

```env
GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
SECRET_KEY=your_random_secret_key_12345
DEBUG=True
```

**Important:** Replace `your_random_secret_key_12345` with a random string!

### Step 4: Run the Application

```bash
python app.py
```

You should see:

```
============================================================
   Nexus Assistant - Georgian Law Database
============================================================
   Total Laws Loaded: 38
   Gemini API Status: ✓ Configured
============================================================

   Starting Flask server...
   Open http://localhost:5000 in your browser
```

### Step 5: Open in Browser

Navigate to: **http://localhost:5000**

## 🎯 Testing the Application

### Test 1: Browse Laws

1. Click "კანონები" in the navigation
2. You should see all 38 laws with:
   - Georgian title
   - English summary
   - English keywords
3. Try searching for "police" or "prosecutor"

### Test 2: AI Assistant

1. Click "AI ასისტენტი"
2. Ask a question in Georgian, for example:
   - "რა უფლებები აქვს პროკურატურას?"
   - "როგორ მუშაობს პოლიცია?"
   - "რა არის იმუნიტეტი?"
3. Wait for AI response (5-10 seconds)
4. Check that sources are listed

### Test 3: View Law Details

1. From browse page, click "სრული ტექსტი" on any law
2. You should see:
   - Full Georgian text
   - English summary
   - Keywords

## 🔧 Troubleshooting

### Problem: "Gemini API არ არის კონფიგურირებული"

**Solution:**
1. Check `.env` file exists
2. Verify `GEMINI_API_KEY` is set correctly
3. Restart the application

### Problem: No laws appear

**Solution:**
1. Check `laws/` folder contains .txt files
2. Verify files have `---METADATA---` section
3. Check terminal for error messages

### Problem: Georgian text shows as "??????"

**Solution:**
1. Ensure all .txt files are UTF-8 encoded
2. Your browser should support Georgian fonts
3. Check that Noto Sans Georgian font loads

### Problem: AI responds in English

**Solution:**
- This is a Gemini model behavior issue
- The prompt requests Georgian responses
- Try rephrasing your question in Georgian

## 📊 Verification Checklist

Before using, verify:

- [ ] All 38 law files in `laws/` folder
- [ ] Each file has `---METADATA---` section
- [ ] `.env` file created with valid Gemini API key
- [ ] Python dependencies installed
- [ ] Application starts without errors
- [ ] Browse page shows all 38 laws
- [ ] Search functionality works
- [ ] Chat interface loads
- [ ] AI responds to Georgian questions

## 🎓 How to Use

### For Browsing Laws:

1. **View All Laws:** Click "კანონები"
2. **Search:** Type keywords in search box (English or Georgian)
3. **View Details:** Click "სრული ტექსტი →" button
4. **Go Back:** Click "← უკან კანონების სიაში"

### For AI Assistant:

1. **Start Chat:** Click "AI ასისტენტი"
2. **Ask Question:** Type in Georgian (e.g., "რა არის პროკურატურის უფლებამოსილება?")
3. **Submit:** Press Enter or click "გაგზავნა"
4. **View Answer:** AI responds with law citations
5. **Clear History:** Click "ისტორიის წაშლა" if needed

## 🚨 Important Notes

### API Usage (Free Tier):
- 15 requests/minute
- 1,500 requests/day
- 1 million tokens/month

The app is optimized to stay within these limits by:
- Only sending 2-5 most relevant laws per question
- Using keyword matching before AI calls
- Limiting law text to 3000 characters

### Data Privacy:
- Conversations stored in session (temporary)
- Cleared when browser closes or "Clear History" clicked
- No data sent to external servers except Gemini API

### Performance:
- First load: 2-3 seconds (loads all 38 laws)
- Browse page: Instant
- AI response: 5-15 seconds (depends on Gemini API)
- Search: Instant (keyword matching)

## 📁 File Overview

**Core Application:**
- `app.py` - Main Flask application with routes
- `law_parser.py` - Parses law files and metadata
- `gemini_helper.py` - Handles Gemini API integration
- `config.py` - Configuration settings

**Frontend:**
- `templates/` - HTML pages (Jinja2 templates)
- `static/css/style.css` - All styling
- `static/js/main.js` - General JavaScript
- `static/js/chat.js` - Chat functionality

**Data:**
- `laws/` - 38 Georgian law files with metadata

**Configuration:**
- `.env` - Your API keys (create this!)
- `requirements.txt` - Python dependencies

## 🔄 Updating Laws

To update metadata for laws:

1. Edit the law file in `laws/` folder
2. Modify text after `---METADATA---`
3. Save with UTF-8 encoding
4. Restart application

To add new laws:

1. Create `laws/new-law.txt`
2. First line: Georgian law name
3. Add Georgian text
4. Add metadata section
5. Restart application

## ✨ Features Explained

### Smart Search:
- Searches Georgian titles
- Searches English summaries
- Searches English keywords
- Shows matching laws instantly

### Two-Step AI:
1. **Step 1:** Find relevant laws using English metadata
2. **Step 2:** Send only relevant laws to Gemini for answer

Benefits:
- Faster responses
- Lower API costs
- More accurate answers
- Stays within free tier

### Responsive Design:
- Works on phones (320px+)
- Works on tablets (768px+)
- Works on desktops (1200px+)
- Georgian fonts load properly

## 🆘 Getting Help

If something doesn't work:

1. Check terminal for error messages
2. Verify `.env` file configuration
3. Ensure Python 3.8+ is installed
4. Check all dependencies are installed
5. Verify law files have proper format

## 🎉 You're Ready!

The application is fully functional and ready to use!

**Next steps:**
1. Run `python app.py`
2. Open http://localhost:5000
3. Start browsing laws or asking questions!

---

**Have fun with Nexus Assistant! 🏛️**
