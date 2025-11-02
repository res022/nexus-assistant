# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Nexus Assistant** is a Flask-based web application that provides AI-powered assistance and quiz testing for Georgian law documents. It features:
- AI chat assistant using Google Gemini 2.0 Flash API (sources hidden from users)
- AI-generated quiz questions from 38 Georgian law documents
- Statistics tracking for quiz performance
- 1,348+ pre-generated quiz questions
- **Minimalist Legal Design**: Professional navy (#1a1f36) and gold (#f4b740) color scheme with serif typography
- **Secure Quiz System**: Correct answers not sent to frontend to prevent cheating
- **Shared Quiz System**: Admins can create shareable quizzes with one-time attempt restrictions

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

**Problem:** Quiz explanations not showing
- **Cause:** Security fix removed explanations for correct answers
- **Fix:** Always send explanation and law_reference, only hide correct_answer when user answers correctly

## Recent Changes & Updates (2025-11-01)

### Design System Overhaul - Minimalist Legal Theme

The entire application has been redesigned with a professional minimalist legal aesthetic:

**Color Scheme:**
- Primary Navy: `#1a1f36` - Headers, navigation, admin panel
- Accent Gold: `#f4b740` - Borders, hover states, CTAs
- Light Background: `#fafafa` - Page backgrounds
- White: `#ffffff` - Cards, forms, content areas
- Text Dark: `#2d3748` - Body text
- Text Muted: `#718096` - Secondary text

**Typography:**
- **Headings**: 'Playfair Display' (serif) - Professional, legal feel
- **Body**: 'Inter' (sans-serif) - Clean, modern readability
- **Georgian Support**: 'Noto Sans Georgian', 'Sylfaen', 'BPG Arial'

**Files Updated:**
- `static/css/style.css` - Complete redesign (v7)
- `templates/base.html` - Added new font imports, reorganized navigation
- `templates/admin/base.html` - Matching admin panel design
- `templates/user/login.html` - Applied minimalist legal design
- `templates/user/register.html` - Applied minimalist legal design

### Security Enhancements

**1. Quiz Answer Security (Prevent Cheating)**

Problem: Users could inspect element to see correct answers before submitting.

Solution: Server-side conditional data sending
- Correct answer is ONLY sent to frontend when user answers incorrectly
- When user answers correctly, only `is_correct: true` is sent
- Explanations and law references are ALWAYS sent for learning purposes
- Frontend cannot access correct answer through inspect element when answering correctly

**Files Modified:**
- `app.py:466-481` - Modified `/api/quiz/answer` endpoint response logic
- `static/js/quiz.js:135-161` - Updated feedback display to handle conditional data

**Implementation:**
```python
# Backend (app.py)
response_data = {
    'is_correct': is_correct,
    'user_answer': user_answer,
    'explanation': explanation,  # Always send for learning
    'law_reference': law_reference,  # Always send for context
    # ... other fields
}

# Only include correct_answer if answered incorrectly
if not is_correct:
    response_data['correct_answer'] = correct_answer
```

**2. AI Chat Sources Hidden**

Sources from laws/rules are no longer displayed in chat responses to provide cleaner UX.

**Files Modified:**
- `templates/chat.html` - Removed source citation display
- `static/js/chat.js` - Removed source rendering logic

### Content Display Changes

**1. Georgian-Only Law Display**

All law browsing and detail pages now display only Georgian text, removing English summaries and keywords.

**Files Modified:**
- `templates/browse.html` - Removed English summary and keywords from law cards
- `templates/law_detail.html` - Removed English summary section, shows only Georgian text

**2. Navigation Reorganization**

Navigation has been split into two sections:
- **Left**: Main navigation links (მთავარი, კანონები, ჩატი, ქვიზი, etc.)
- **Right**: Authentication links (შესვლა, რეგისტრაცია)

**Files Modified:**
- `templates/base.html:32-60` - Reorganized navbar structure with flex layout

### Database Expansion - Shared Quiz System

**New Tables Added:**

1. **shared_quizzes**:
   - `id` - Primary key
   - `quiz_id` - Unique quiz identifier (TEXT)
   - `title` - Quiz title
   - `description` - Quiz description
   - `question_ids` - JSON array of question IDs
   - `created_by_admin` - Admin username
   - `created_at` - Creation timestamp
   - `is_active` - Active/inactive status

2. **shared_quiz_attempts**:
   - `id` - Primary key
   - `quiz_id` - Foreign key to shared_quizzes
   - `user_id` - User who attempted quiz
   - `score` - Number of correct answers
   - `total_questions` - Total questions in quiz
   - `answers_json` - JSON of user's answers
   - `completed_at` - Completion timestamp
   - `can_retake` - Admin-controlled retake permission
   - **UNIQUE constraint**: (quiz_id, user_id) - Prevents multiple attempts

**New Database Methods:**

Added 10 new methods to `database.py` for shared quiz management:
- `create_shared_quiz()` - Create new shareable quiz
- `get_shared_quiz()` - Get quiz details by ID
- `get_shared_quiz_questions()` - Get all questions for a quiz
- `check_user_attempt()` - Check if user already attempted quiz
- `record_shared_quiz_attempt()` - Record quiz completion
- `allow_retake()` - Admin allows user to retake
- `get_quiz_attempts()` - View all attempts (admin view)
- `get_all_shared_quizzes()` - List all shared quizzes
- `toggle_quiz_active()` - Activate/deactivate quiz

**Files Modified:**
- `database.py:74-441` - Added shared quiz infrastructure

### UI Component Updates

**Buttons:**
- Primary buttons: Transparent with gold border, fills gold on hover
- Secondary buttons: White with border, subtle hover effects
- Disabled state: Grayed out with cursor not-allowed

**Cards:**
- White background with light gray border
- Gold top border (4px) for emphasis
- Subtle box shadow on hover

**Forms:**
- Clean input fields with gold focus border
- Consistent padding and spacing
- Validation hints in muted text

**Tables (Admin):**
- Navy header with white text
- Alternating row colors for readability
- Gold hover highlight on rows

### File Structure Updates

**New Files Created:**
None - all changes were modifications to existing files

**Files Modified Summary:**
1. `static/css/style.css` - Complete design overhaul
2. `templates/base.html` - Navigation reorganization, font imports
3. `templates/admin/base.html` - Admin panel redesign
4. `templates/user/login.html` - New minimalist legal design
5. `templates/user/register.html` - New minimalist legal design
6. `templates/chat.html` - Removed source citations
7. `templates/browse.html` - Georgian-only display
8. `templates/law_detail.html` - Georgian-only display
9. `static/js/chat.js` - Removed source rendering
10. `static/js/quiz.js` - Updated feedback display logic
11. `app.py` - Quiz security enhancements
12. `database.py` - Shared quiz system infrastructure

### Updated Statistics

- **Total Questions**: 1,348 (increased from 1,012)
- **Total Laws**: 38 Georgian law documents
- **Total Server Rules**: 22 documents
- **Design Version**: v7 (minimalist legal theme)
- **Security Level**: Enhanced (quiz answer protection)

### Shared Quiz System - Complete Implementation

**Status**: ✅ Fully Functional

The shareable quiz system allows admins to create custom quizzes with specific questions and share them with users via unique URLs.

#### Features:

1. **Admin Quiz Creation** (`/admin/quiz/create`):
   - Select existing questions from database with filters (source type, difficulty)
   - Create fully custom questions on-the-fly with:
     - Question text
     - Multiple options (2-10 options)
     - Correct answer selection
     - Explanation and law reference
     - Category and difficulty
     - Source type (laws/rules)
   - Mix existing and custom questions in single quiz
   - Set quiz title and description
   - Generate shareable link automatically

2. **Quiz Management Dashboard** (`/admin/quizzes`):
   - View all created quizzes with stats
   - See attempt count for each quiz
   - Toggle quiz active/inactive status
   - Copy shareable links
   - Access results dashboard
   - Statistics overview (total quizzes, attempts, average scores)

3. **Public Quiz Interface** (`/quiz/shared/<quiz_id>`):
   - Users must register/login to access
   - Start screen with quiz rules
   - Progress bar showing current question
   - Question display with category and difficulty badges
   - Neutral answer feedback (no correct/wrong indication)
   - One-time attempt enforcement (database UNIQUE constraint)
   - Results hidden from users (only admin sees scores)
   - Automatic redirect to quiz after login/registration

4. **Admin Results Dashboard** (`/admin/quiz/<quiz_id>/results`):
   - Quiz information and statistics
   - All user attempts with scores
   - Detailed answer viewing for each attempt
   - Allow retake permission management
   - Average score, pass rate calculations
   - Timestamp tracking

#### Security Features:

1. **Answer Privacy**:
   - Users don't see if answers are correct/wrong during quiz
   - Users don't see final scores
   - Only "პასუხი მიღებულია" (Answer received) confirmation shown
   - Prevents collaborative cheating

2. **Attempt Restrictions**:
   - Database UNIQUE constraint on (quiz_id, user_id)
   - One attempt per user by default
   - Admin can allow retakes via dashboard
   - Prevents multiple submissions

3. **Authentication Requirements**:
   - Unauthenticated users redirected to login
   - `next` parameter preserves quiz URL
   - After login/register, user returns to quiz automatically

#### Implementation Details:

**Files Created:**
- `templates/admin/create_quiz.html` - Quiz creation interface (732 lines)
- `templates/admin/quizzes.html` - Quiz management dashboard (432 lines)
- `templates/admin/quiz_results.html` - Results viewing interface (388 lines)
- `templates/shared_quiz.html` - Public quiz-taking interface (518 lines)

**Files Modified:**
- `app.py` - Added 10 new routes:
  - `/admin/quizzes` - Quiz list
  - `/admin/quiz/create` - Create quiz page
  - `/admin/api/questions` - Question API
  - `/admin/api/quiz/create` - Create quiz API
  - `/admin/api/quiz/toggle` - Toggle active status
  - `/admin/quiz/<quiz_id>/results` - Results page
  - `/admin/api/quiz/allow-retake` - Allow retake
  - `/admin/api/quiz/attempt/<attempt_id>` - Get attempt details
  - `/quiz/shared/<quiz_id>` - Public quiz page
  - `/api/quiz/shared/submit` - Submit quiz
- `database.py` - Added `question_ids` to `get_all_shared_quizzes()`
- `templates/user/login.html` - Added `next` parameter handling
- `templates/user/register.html` - Added `next` parameter handling
- `templates/admin/base.html` - Added "🎯 Shared Quizzes" navigation link

**Key Technical Fixes:**

1. **Event Listener Performance** (create_quiz.html:664-677):
   - Problem: Event listeners being added repeatedly causing lag
   - Solution: Event delegation on parent container
   - Impact: Eliminated lag when typing in option fields

2. **Login Redirect Preservation** (app.py:544-577):
   - Problem: Users redirected to dashboard instead of quiz after login
   - Solution: `next` parameter handling in login/register routes
   - Impact: Seamless authentication flow

3. **User Feedback Privacy** (shared_quiz.html:417-450):
   - Problem: Users seeing correct/wrong answers
   - Solution: Neutral feedback only, no correctness indication
   - Impact: Prevents answer sharing, maintains quiz integrity

4. **Score Privacy** (shared_quiz.html:508-515):
   - Problem: Users seeing their scores
   - Solution: Hide score, show only thank you message
   - Impact: Only admin can view results

#### Database Schema:

**shared_quizzes table:**
```sql
CREATE TABLE shared_quizzes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    question_ids TEXT NOT NULL,  -- JSON array
    created_by_admin TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
)
```

**shared_quiz_attempts table:**
```sql
CREATE TABLE shared_quiz_attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    quiz_id TEXT NOT NULL,
    user_id INTEGER NOT NULL,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    answers_json TEXT NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    can_retake INTEGER DEFAULT 0,
    FOREIGN KEY (quiz_id) REFERENCES shared_quizzes(quiz_id),
    UNIQUE(quiz_id, user_id)  -- One attempt per user
)
```

#### Usage Flow:

1. Admin creates quiz at `/admin/quiz/create`
2. Admin shares quiz URL: `/quiz/shared/<quiz_id>`
3. User visits URL (may need to login/register)
4. User takes quiz (answers hidden, one attempt)
5. User sees thank you message (no score)
6. Admin views results at `/admin/quiz/<quiz_id>/results`
7. Admin can allow retake if needed

#### Performance Optimizations:

- Event delegation for dynamic option inputs
- Database indexes on quiz_id and user_id
- JSON storage for flexible question/answer data
- Session-based state management
- Minimal data sent to frontend (security + performance)

#### Error Handling:

- Quiz not found → 404 page
- Already attempted → Redirect with error message
- Not logged in → Redirect to login with `next` parameter
- Invalid quiz_id → Error page
- Database errors → Graceful error messages

**Last Updated:** 2025-11-01 (Session: Shared Quiz System Implementation)