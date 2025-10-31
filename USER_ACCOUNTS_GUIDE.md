# User Accounts System - Complete Guide

Complete documentation for the user accounts and authentication system in Nexus Assistant.

---

## ✨ Features Overview

The user accounts system provides:

✅ **User Registration** - Create accounts with username, email, password
✅ **User Login/Logout** - Secure authentication with password hashing
✅ **User Dashboard** - Personal statistics and performance tracking
✅ **Quiz History** - Permanent quiz history linked to user accounts
✅ **Leaderboard** - Global rankings by accuracy and performance
✅ **Profile Page** - View account details and overall stats
✅ **Session Management** - Secure session-based authentication
✅ **Navigation Integration** - User menu in navigation bar

---

## 🗄️ Database Schema

### Users Table
```sql
users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name TEXT,
    created_at TIMESTAMP,
    last_login TIMESTAMP,
    is_active INTEGER DEFAULT 1,
    total_quizzes INTEGER DEFAULT 0,
    total_correct INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0
)
```

### User Quiz Sessions Table
```sql
user_quiz_sessions (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    total_questions INTEGER,
    correct_answers INTEGER
)
```

### User Quiz Answers Table
```sql
user_quiz_answers (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    session_id INTEGER,
    question_id INTEGER NOT NULL,
    user_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL,
    answered_at TIMESTAMP
)
```

---

## 🔐 Security Features

### Password Hashing
- Uses SHA-256 with unique salt per user
- Format: `{salt}${hash}`
- Never stores plain text passwords
- Salts are 32 characters (16 bytes hex)

### Session Management
- Flask session-based authentication
- Session data stored in secure cookies
- User ID, username, display name stored in session
- Automatic session expiration on logout

### Input Validation
- Username: Minimum 3 characters
- Email: Must contain @ symbol
- Password: Minimum 6 characters
- Password confirmation match required

---

## 📍 User Routes

### Registration
**URL:** `/register`
**Method:** GET, POST
**Template:** `user/register.html`

**Form Fields:**
- username (required, min 3 chars)
- email (required, valid email)
- password (required, min 6 chars)
- confirm_password (required, must match)
- display_name (optional)

**Success:** Redirects to `/login`
**Error:** Shows flash message, stays on registration page

### Login
**URL:** `/login`
**Method:** GET, POST
**Template:** `user/login.html`

**Form Fields:**
- username (can be username or email)
- password

**Success:** Redirects to `/dashboard`
**Error:** Shows flash message

**Session Data Set:**
- `user_id`: User's database ID
- `username`: Username
- `display_name`: Display name

### Logout
**URL:** `/logout`
**Method:** GET
**Action:** Clears session, redirects to home

### Dashboard
**URL:** `/dashboard`
**Method:** GET
**Auth:** Login required
**Template:** `user/dashboard.html`

**Data Displayed:**
- Total quizzes completed
- Total questions answered
- Total correct answers
- Overall accuracy percentage
- Performance by category
- Performance by difficulty
- Recent quiz sessions (last 10)

### Profile
**URL:** `/profile`
**Method:** GET
**Auth:** Login required
**Template:** `user/profile.html`

**Data Displayed:**
- Username
- Email
- Display name
- Registration date
- Last login
- Quick stats (quizzes, correct, accuracy)

### Leaderboard
**URL:** `/leaderboard`
**Method:** GET
**Auth:** Public (no login required)
**Template:** `user/leaderboard.html`

**Features:**
- Top 20 users by accuracy
- Minimum 10 questions answered to appear
- Shows: rank, username, quizzes, questions, correct, accuracy
- Top 3 get medal emojis (🥇🥈🥉)

---

## 🎮 Quiz Integration

### Quiz Start
When a quiz starts:
1. Check if user is logged in
2. If yes: Create `user_quiz_sessions` record
3. Store session ID in Flask session
4. Questions proceed normally

### Quiz Answer
When user answers a question:
1. Check if user is logged in
2. If yes: Save to `user_quiz_answers` table
3. Update user's total_correct and total_questions
4. If no: Use session-based tracking (old system)

### Quiz Complete
When quiz finishes:
1. Update `user_quiz_sessions` with completion time
2. Update user's `total_quizzes` counter
3. Calculate final statistics

---

## 📊 Statistics Calculation

### Overall Stats
- **Total Quizzes:** Count of completed quiz sessions
- **Total Questions:** Sum of all questions answered
- **Total Correct:** Sum of all correct answers
- **Accuracy:** (total_correct / total_questions) × 100

### Category Breakdown
```python
SELECT category, COUNT(*), SUM(is_correct)
FROM user_quiz_answers
JOIN quiz_questions ON question_id = id
WHERE user_id = ?
GROUP BY category
```

### Difficulty Breakdown
```python
SELECT difficulty, COUNT(*), SUM(is_correct)
FROM user_quiz_answers
JOIN quiz_questions ON question_id = id
WHERE user_id = ?
GROUP BY difficulty
```

### Leaderboard Calculation
```python
SELECT username, display_name, total_quizzes,
       total_correct, total_questions,
       (total_correct / total_questions * 100) as accuracy
FROM users
WHERE total_questions >= 10
ORDER BY accuracy DESC, total_questions DESC
LIMIT 20
```

---

## 🎨 UI/UX Features

### Navigation Bar
**When Not Logged In:**
- Shows "შესვლა" (Login) link
- Shows "რეგისტრაცია" (Register) button (green)
- Shows "🏆 ლიდერბორდი" (Leaderboard) link

**When Logged In:**
- Shows user display name with dropdown
- Dropdown contains:
  - 📊 Dashboard
  - 👤 პროფილი (Profile)
  - გასვლა (Logout)
- Shows "🏆 ლიდერბორდი" (Leaderboard) link

### Dashboard
- **Stats Cards:** 4 gradient cards showing key metrics
- **Category Table:** Sortable table with color-coded accuracy
- **Difficulty Table:** Performance by easy/medium/hard
- **Recent Sessions:** Last 10 quiz sessions with dates
- **Quick Actions:** Buttons to start quiz, view leaderboard, use AI

### Profile
- **Avatar:** Large circular gradient with first letter
- **User Info:** Username, email, registration date, last login
- **Quick Stats:** 3 stat cards (quizzes, correct, accuracy)
- **Actions:** Back to dashboard, logout

### Leaderboard
- **Top 3 Highlight:** Gold background for top 3
- **Medal Emojis:** 🥇🥈🥉 for top 3
- **Color-Coded Accuracy:**
  - 90%+: Green background
  - 80-89%: Blue background
  - 70-79%: Yellow background
  - <70%: Red background

---

## 🔧 Technical Implementation

### UserManager Class
**Location:** `user_manager.py`

**Key Methods:**
- `create_user()` - Register new user
- `authenticate_user()` - Login validation
- `get_user_by_id()` - Fetch user data
- `get_user_stats()` - Calculate statistics
- `record_quiz_answer()` - Save quiz answer
- `start_quiz_session()` - Begin quiz tracking
- `complete_quiz_session()` - Finish quiz tracking
- `get_leaderboard()` - Fetch top users

### Decorators
**`@user_login_required`**
- Checks if `user_id` exists in session
- Redirects to `/login` if not logged in
- Use on protected routes

**Example:**
```python
@app.route('/dashboard')
@user_login_required
def user_dashboard():
    # Only logged-in users can access
    pass
```

### Password Hashing
```python
def hash_password(password):
    salt = secrets.token_hex(16)  # 32 char salt
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"

def verify_password(password, password_hash):
    salt, pwd_hash = password_hash.split('$')
    return pwd_hash == hashlib.sha256((password + salt).encode()).hexdigest()
```

---

## 📝 Usage Examples

### Creating a User Account
1. Visit `/register`
2. Fill in form:
   - Username: `john_doe`
   - Email: `john@example.com`
   - Display Name: `John Doe`
   - Password: `password123`
   - Confirm Password: `password123`
3. Click "შექმენით ანგარიში"
4. Redirected to login page
5. Login with credentials

### Taking a Quiz as Logged-In User
1. Login to account
2. Go to Quiz page
3. Start quiz (10 questions)
4. Answer all questions
5. Results automatically saved to account
6. View statistics on Dashboard
7. Quiz appears in "Recent Sessions"

### Viewing Your Statistics
1. Login to account
2. Click on your name in navigation
3. Select "📊 Dashboard"
4. See all your performance data:
   - Total quizzes completed
   - Overall accuracy
   - Performance by category
   - Performance by difficulty
   - Recent quiz history

### Checking Your Rank
1. Visit `/leaderboard` (login not required)
2. Find your position in the rankings
3. See how you compare to others
4. Minimum 10 questions needed to appear

---

## 🚀 Deployment Notes

### Database Migration
The database tables are created automatically on first run via `user_manager._initialize_database()`.

No manual migration needed!

### Session Storage
- Flask sessions stored in browser cookies
- Max cookie size: 4093 bytes
- User data minimal to avoid size issues
- Only stores: user_id, username, display_name

### Performance
- Database: SQLite (good for 100s of users)
- Queries optimized with indexes
- Statistics cached in users table
- Leaderboard limited to top 20

### Scaling Considerations
For 1000+ users:
- Consider PostgreSQL instead of SQLite
- Add database connection pooling
- Cache leaderboard results
- Add pagination to dashboard history

---

## 🔄 User Flow Diagrams

### Registration Flow
```
User visits /register
  ↓
Fills registration form
  ↓
Validates input (min lengths, email format)
  ↓
Checks username/email uniqueness
  ↓
Hashes password with salt
  ↓
Saves to users table
  ↓
Redirects to /login
  ↓
User logs in with credentials
```

### Login Flow
```
User visits /login
  ↓
Enters username (or email) + password
  ↓
Queries users table for username/email
  ↓
Verifies password hash
  ↓
Creates Flask session with user data
  ↓
Redirects to /dashboard
```

### Quiz with Account Flow
```
Logged-in user starts quiz
  ↓
Creates user_quiz_sessions record
  ↓
For each answer:
  - Saves to user_quiz_answers
  - Updates user total_questions
  - Updates user total_correct (if correct)
  ↓
Quiz completes
  ↓
Updates user_quiz_sessions (completed_at, totals)
  ↓
Updates user total_quizzes
  ↓
User can view stats on Dashboard
```

---

## 🐛 Troubleshooting

### Can't Register - "Username already exists"
**Cause:** Username is taken
**Solution:** Choose a different username

### Can't Register - "Email already exists"
**Cause:** Email is taken
**Solution:** Use a different email or login instead

### Can't Login - "Invalid username or password"
**Causes:**
1. Wrong password
2. Username doesn't exist
3. Using email but system expects username (or vice versa)

**Solution:** Try using email if username doesn't work, and vice versa

### Dashboard Shows 0 Quizzes
**Causes:**
1. Haven't taken any quizzes yet
2. Quizzes taken before creating account

**Solution:** Take a new quiz while logged in

### Not on Leaderboard
**Causes:**
1. Less than 10 questions answered
2. Other users have higher accuracy

**Solution:** Answer at least 10 questions, improve accuracy

### Session Expired
**Cause:** Browser closed or cookies cleared
**Solution:** Login again

---

## 📈 Future Enhancements

Possible additions:
- [ ] Password reset via email
- [ ] Email verification
- [ ] Change password functionality
- [ ] Delete account option
- [ ] User avatars (upload images)
- [ ] Achievements/badges system
- [ ] Friends list
- [ ] Private profile option
- [ ] Export statistics to PDF
- [ ] Weekly/monthly leaderboards
- [ ] Category-specific leaderboards
- [ ] Difficulty-specific leaderboards

---

## 🔑 API Integration

### Check if User is Logged In (JavaScript)
```javascript
// Session data is server-side only
// Check by trying to access protected route
fetch('/api/user/check')
  .then(r => r.json())
  .then(data => {
    if (data.logged_in) {
      // User is logged in
      console.log('User:', data.username);
    }
  });
```

### Get Current User Stats (Add this route)
```python
@app.route('/api/user/stats')
@user_login_required
def api_user_stats():
    user_id = session.get('user_id')
    stats = user_manager.get_user_stats(user_id)
    return jsonify(stats)
```

---

## 📚 Files Created

```
user_manager.py                    # User authentication and management
app.py                            # Updated with user routes
templates/user/
  ├── register.html               # Registration page
  ├── login.html                  # Login page
  ├── dashboard.html              # User dashboard
  ├── profile.html                # User profile
  └── leaderboard.html            # Public leaderboard
templates/base.html               # Updated navigation with user menu
USER_ACCOUNTS_GUIDE.md            # This file
```

---

## ✅ Testing Checklist

- [ ] Can register new account
- [ ] Can't register with duplicate username
- [ ] Can't register with duplicate email
- [ ] Password validation works (min 6 chars)
- [ ] Passwords must match
- [ ] Can login with username
- [ ] Can login with email
- [ ] Wrong password shows error
- [ ] Can logout
- [ ] Dashboard shows correct stats
- [ ] Quiz results save to account
- [ ] Leaderboard shows top users
- [ ] Profile displays correct info
- [ ] Navigation shows user menu when logged in
- [ ] Navigation shows login/register when not logged in
- [ ] Protected routes redirect to login
- [ ] Session persists across page reloads

---

## 🎉 Summary

The user accounts system is now **fully functional** with:

✅ **Complete authentication** (registration, login, logout)
✅ **Personal dashboards** with detailed statistics
✅ **Permanent quiz history** linked to accounts
✅ **Global leaderboard** with rankings
✅ **Secure password storage** with hashing
✅ **Session management** with Flask sessions
✅ **Beautiful UI** with gradient cards and responsive design
✅ **Full integration** with existing quiz system

**Users can now:**
- Create accounts and login
- Track their quiz performance over time
- See detailed statistics by category and difficulty
- Compete on the global leaderboard
- View their profile and history
- All data is saved permanently!

---

Made with ❤️ for San Andreas Roleplay Server
