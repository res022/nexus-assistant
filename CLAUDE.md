# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Nexus Assistant** is a Flask-based web application that provides AI-powered assistance and quiz testing for Georgian law documents. It features:
- AI chat assistant using Google Gemini 2.0 Flash API
- AI-generated quiz questions from 38 Georgian law documents
- Statistics tracking for quiz performance
- 1,012+ pre-generated quiz questions

**Critical Language Note:** All source documents are in Georgian language (ქართული ენა). Always handle UTF-8 encoding properly when reading, processing, and outputting Georgian text.

## Repository Structure

```
nexus assistant/
├── laws/                  # 38 Georgian law files (.txt, UTF-8 encoded)
├── templates/            # Flask HTML templates
│   ├── base.html
│   ├── index.html
│   ├── chat.html
│   └── quiz.html
├── static/
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   └── js/
│       └── quiz.js       # Quiz frontend logic
├── app.py                # Flask application (main server)
├── config.py             # Configuration (loads .env)
├── law_parser.py         # Law document parser
├── quiz_generator.py     # AI quiz question generator
├── database.py           # SQLite database handler
├── generate_1000_questions.py  # Script to generate 1000+ questions
├── fill_missing_laws.py  # Script to fill gaps in question generation
├── quiz_data.db          # SQLite database (1,012 questions)
├── .env                  # API keys and config (GEMINI_API_KEY)
└── CLAUDE.md             # This file
```

## Development Workflow

### Running the Application

**Start the Flask server:**
```bash
python app.py
# Runs on http://localhost:5000
```

**Generate quiz questions (if needed):**
```bash
# Generate 1000+ questions in 2 passes
python generate_1000_questions.py

# Fill any missing laws
python fill_missing_laws.py
```

### Key Features

1. **AI Chat Assistant** (`/chat`):
   - Uses Gemini 2.0 Flash API
   - Answers questions about Georgian laws
   - Session-based conversation history
   - Law reference citations

2. **Quiz Mode** (`/quiz`):
   - 1,012 AI-generated questions from all 38 laws
   - Multiple difficulty levels (easy, medium, hard)
   - Categories: arrest, search, warrants, territories, penalties, procedures, rights
   - Statistics tracking per user session
   - Manual next question navigation (green button appears after answering)

3. **Statistics Tracking**:
   - Total questions answered
   - Correct answers
   - Accuracy percentage
   - Performance by category

### API Configuration

**Gemini API Setup (.env file):**
```env
GEMINI_API_KEY=AIzaSyCGfeY_Q1emufh5xs0qp-DMOf4tX-khaKQ
SECRET_KEY=nexus_assistant_secret_key_2025_san_andreas_roleplay
DEBUG=True
```

**API Details:**
- Model: `gemini-2.0-flash`
- Google Cloud project with $300 credit
- Rate limits: 60+ requests/minute (paid tier)
- Cost: ~$0.001 per chat conversation

### Important Technical Notes

1. **UTF-8 Encoding (Windows Console Issues):**
   - Windows console uses cp1252 encoding
   - **NEVER** print Georgian text directly to console - it will crash
   - Always avoid: `print(f"Law: {georgian_law_name}")`
   - Instead use: `print(f"Law: {filename} ({len(text)} chars)")`

2. **Session Management (Critical Fix):**
   - Flask sessions have 4096 byte browser cookie limit
   - **NEVER** store full question data in session
   - Store only question IDs: `session['quiz'] = {'question_ids': [1,2,3]}`
   - Fetch full question from database when needed

3. **Quiz Question Storage:**
   - All 1,012 questions pre-generated in `quiz_data.db`
   - SQLite database with tables: `quiz_questions`, `user_progress`, `quiz_history`
   - Questions include: question_text, options (JSON), correct_answer, explanation, law_reference, category, difficulty

4. **File Reading:**
   - All files in `laws/` are UTF-8 encoded Georgian text
   - Use `codecs.open(file, 'r', encoding='utf-8')` in Python
   - Law name is always on the **first line** of each .txt file

## Recent Changes & Fixes

### Session 2025-10-31:
1. **Fixed quiz answer submission bug**:
   - Problem: Session cookie exceeded 4096 byte limit
   - Solution: Store only question IDs in session, fetch full data from DB

2. **Generated 1,012 quiz questions**:
   - 2-pass generation: 487 + 499 questions
   - Fill script added 26 questions for missing law
   - All 38 laws now covered

3. **Fixed stats display**:
   - Problem: Stats didn't update after quiz
   - Solution: Reload page after quiz completion

4. **Improved quiz UX**:
   - Removed automatic 3-second transition
   - Added manual green "Next Question" button at top
   - Button only appears after answering
   - Users can read explanations at their own pace

5. **Fixed encoding issues**:
   - Avoided printing Georgian text to Windows console
   - All scripts now use filename/length instead of law names in output

## Architecture & Data Flow

### Flask Application Flow

```
User Request → Flask Routes → Business Logic → Database/API → Response

Routes:
  / (index.html)           → Landing page
  /chat                    → AI assistant chat interface
  /quiz                    → Quiz mode with statistics
  /api/chat                → POST: Send message to AI
  /api/quiz/start          → POST: Start new quiz session
  /api/quiz/answer         → POST: Submit answer, get feedback

Session Data:
  - conversation_history   → List of chat messages
  - current_quiz          → {question_ids: [1,2,3], current_index: 0}
  - session_id            → Unique user identifier
```

### Georgian Legal Document Structure

Georgian laws follow this typical structure:
- **კანონი** (Law) - Title on first line
- **თავი** (Chapter) - Major divisions (e.g., "თავი I", "თავი II")
- **მუხლი** (Article) - Individual articles (e.g., "მუხლი 4", "მუხლი 15")
- **ნაწილი** (Part/Section) - Subsections (e.g., "ნაწილი 1", "7.1")
- **პუნქტი** (Point) - Individual points/paragraphs

### Key Legal Terms

- **პროკურატურა** - Prosecutor's Office
- **გენერალური პროკურორი** - Attorney General / Prosecutor General
- **პროკურორი** - Prosecutor
- **უფლებამოსილება** - authority/power/permission
- **ფუნქცია** - function
- **უფლება** - right
- **მოვალეობა** - duty/obligation
- **კომპეტენცია** - competence
- **საქმიანობა** - activity

## HTML Output Requirements

Generated HTML must:
- Use UTF-8 encoding with proper `<meta charset="UTF-8">`
- Include Georgian-compatible fonts: `font-family: 'BPG Arial', 'Sylfaen', 'Noto Sans Georgian', sans-serif;`
- Set language attribute: `<html lang="ka">`
- Display each permission with:
  - Law name (from first line of file)
  - Exact sentence containing the permission
  - Article/section reference
  - Source filename
  - Surrounding context
- Be mobile-responsive and print-friendly

## Common Legal File Names Reference

- `prokuraturis.txt` - Prosecutor's Office Law (main source)
- `konstitucia.txt` - Constitution
- `saproceso.txt` - Criminal Procedural Code
- `sisxlissamartali.txt` - Criminal Code
- `policiis.txt` - Police Law
- `marshalta.txt` - Marshal Service Law
- `imunitetis.txt` - Immunity Law
- `terorizmis.txt` - Anti-Terrorism Law

## Text Encoding Best Practices

When working with Georgian text:
- Always specify UTF-8 encoding explicitly
- Test Georgian character display before processing large batches
- Georgian has no uppercase/lowercase distinction (no case-insensitive search needed)
- Word boundaries work differently than English
- Some legal terms may be Russian loanwords (transliterated to Georgian)

## Deployment Notes

### Running Locally:
```bash
cd "C:\Users\mrluk\Desktop\nexus assistant"
python app.py
# Access at http://localhost:5000
```

### Google Cloud VM Deployment (Future):
- Can use $300 Google Cloud credit
- Recommended: e2-small instance (~$10/month)
- Install: Python, Flask, Nginx
- Use gunicorn for production: `gunicorn -w 4 -b 0.0.0.0:8000 app:app`
- Configure Nginx as reverse proxy
- API costs are negligible with pre-generated questions

### Database:
- `quiz_data.db` - 1,012 pre-generated questions
- Shared across all users
- Statistics are per-session (not persistent across devices)

## Troubleshooting

**Problem:** Quiz shows "კითხვა ვერ მოიძებნა" (question not found)
- **Cause:** Session cookie too large
- **Fix:** Ensure session only stores question IDs, not full data

**Problem:** Python script crashes with UnicodeEncodeError
- **Cause:** Trying to print Georgian text to Windows console
- **Fix:** Print filename/length instead of Georgian text

**Problem:** Stats don't update after quiz
- **Cause:** Page not refreshing
- **Fix:** Reload page or add `window.location.reload()` in JS

**Problem:** API rate limit errors (429)
- **Cause:** Too many requests to Gemini API
- **Fix:** Add delays between requests (10 seconds), use paid tier
