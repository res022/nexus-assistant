# Admin Panel Guide

Complete guide for using the Nexus Assistant Admin Panel.

---

## 🔐 Access Information

**Login URL:** `http://YOUR_SITE/admin/login`

**Default Credentials:**
- **Username:** `admin`
- **Password:** `nexus2025!`

**⚠️ IMPORTANT:** Change the password in `.env` file before deploying to production!

---

## 📋 Features Overview

The admin panel provides complete control over:

1. **Dashboard** - View statistics and analytics
2. **Law Management** - Add, edit, delete Georgian laws
3. **Question Management** - Manage quiz questions
4. **Content Moderation** - Enable/disable questions

---

## 🎯 How to Access Admin Panel

### Locally (Development):
1. Start application: `python app.py`
2. Open browser: `http://localhost:5000/admin/login`
3. Login with credentials above

### On Production Server:
1. Visit: `http://YOUR_DOMAIN/admin/login`
2. Or: `http://YOUR_SERVER_IP/admin/login`
3. Login with credentials

---

## 📊 Dashboard

**URL:** `/admin/dashboard`

**Features:**
- View total laws count
- View total quiz questions
- See laws with metadata
- View coverage percentage
- Questions breakdown by category
- Questions breakdown by difficulty
- Quick action buttons

---

## 📚 Law Management

### View All Laws

**URL:** `/admin/laws`

**Features:**
- See all 38 Georgian laws
- Check which laws have metadata (English summaries)
- Quick actions: View, Edit, Delete

### Add New Law

**URL:** `/admin/laws/add`

**Steps:**
1. Click "➕ Add New Law" button
2. Fill in form:
   - **Filename:** e.g., `new_law.txt` (must end with .txt)
   - **Law Name:** Georgian law title
   - **Content:** Full Georgian law text
   - **Summary (English):** Brief summary in English
   - **Keywords (English):** Comma-separated keywords
3. Click "💾 Save Law"
4. Law is added and appears in Browse page

**Example:**
```
Filename: immigration.txt
Law Name: საქართველოს კანონი მიგრაციის შესახებ
Content: [Full Georgian law text...]
Summary: This law regulates immigration procedures...
Keywords: immigration, migration, visa, border, entry
```

### Edit Existing Law

**URL:** `/admin/laws/edit/<filename>`

**Steps:**
1. Go to "Manage Laws"
2. Click "✏️ Edit" next to the law
3. Modify any field:
   - Law name (Georgian title)
   - Content (Georgian text)
   - Summary (English)
   - Keywords (English)
4. Click "💾 Save Law"
5. Changes are applied immediately

**Note:** You cannot change the filename when editing. To rename, delete and recreate.

### Delete Law

**Steps:**
1. Go to "Manage Laws"
2. Click "🗑 Delete" next to the law
3. Confirm deletion
4. Law file is removed from system

**⚠️ Warning:** Deletion is permanent! The law file will be deleted from the `laws/` directory.

---

## ❓ Question Management

### View All Questions

**URL:** `/admin/questions`

**Features:**
- See all 1,012+ quiz questions
- Paginated view (50 questions per page)
- Filter by status (Active/Disabled)
- View question details
- Quick actions: Edit, Enable/Disable, Delete

**Question Information:**
- ID number
- Question text (first 100 characters)
- Category badge
- Difficulty level
- Law reference
- Status (Active/Disabled)

### Edit Question

**URL:** `/admin/questions/edit/<id>`

**Steps:**
1. Go to "Manage Questions"
2. Click "✏️ Edit" next to question
3. Modify fields:
   - **Question Text:** The question in Georgian
   - **Option A, B, C, D:** Answer choices
   - **Correct Answer:** Select A, B, C, or D
   - **Difficulty:** Easy, Medium, or Hard
   - **Category:** Question category
   - **Explanation:** Explanation in Georgian
4. Click "💾 Save Changes"

**Example Edit:**
```
Question: რა არის პროკურორის უფლებამოსილება?
Option A: დაკითხვის ჩატარება
Option B: პატიმრობის დაკისრება
Option C: სასამართლო განხილვა
Option D: სამართალწარმოების ინიციირება
Correct Answer: D
Difficulty: Medium
Category: prosecutor
Explanation: პროკურორს აქვს უფლებამოსილება...
```

### Enable/Disable Question

**Steps:**
1. Go to "Manage Questions"
2. Click "🔒 Disable" or "✅ Enable" button
3. Question status is toggled
4. Disabled questions don't appear in quiz

**Use Cases:**
- Disable questions with errors
- Temporarily remove confusing questions
- Keep database intact while hiding from users

### Delete Question

**Steps:**
1. Go to "Manage Questions"
2. Click "🗑" button
3. Confirm deletion
4. Question is permanently removed

**⚠️ Warning:** Cannot be undone!

---

## 🔒 Security Features

### Authentication
- Session-based login
- Password-protected routes
- Auto-logout on browser close
- Login required for all admin pages

### Password Management
- Default password: `nexus2025!`
- **Change in production:**
  1. Edit `.env` file
  2. Update `ADMIN_PASSWORD=your_new_password`
  3. Restart application

### Access Control
- Only logged-in admins can access `/admin/*` routes
- Regular users redirected to login page
- Session expires after logout

---

## 🎨 Admin Panel Design

### Color Scheme
- **Primary:** Blue (#3498db) - Action buttons
- **Success:** Green (#2ecc71) - Success messages, add buttons
- **Warning:** Orange (#f39c12) - Edit buttons, warnings
- **Danger:** Red (#e74c3c) - Delete buttons, errors
- **Dark:** Dark Blue (#2c3e50) - Header, navigation

### Layout
- **Header:** Logo, username, quick links
- **Navigation:** Dashboard, Laws, Questions
- **Content:** Main content area with cards/tables
- **Flash Messages:** Success/error notifications at top

### Responsive
- Works on desktop (optimized)
- Works on tablet (responsive grid)
- Mobile-friendly navigation

---

## 📝 Best Practices

### Law Management
1. **Always include metadata** (summary and keywords)
2. **Use descriptive keywords** for better search
3. **Backup before deleting** laws
4. **Test changes** on Browse page after editing

### Question Management
1. **Review AI-generated questions** before enabling
2. **Check correct answers** are accurate
3. **Ensure explanations** are clear and helpful
4. **Use appropriate difficulty** levels
5. **Categorize consistently** for better organization

### Security
1. **Change default password** immediately
2. **Use strong password** (12+ characters, mixed case, numbers, symbols)
3. **Don't share credentials** publicly
4. **Logout after use** on shared computers
5. **Monitor admin access** logs

---

## 🛠️ Troubleshooting

### Can't Login

**Problem:** "Invalid credentials" error

**Solutions:**
1. Check username is `admin` (all lowercase)
2. Check password matches `.env` file
3. Verify `.env` file exists in project root
4. Restart application after changing `.env`

### Changes Not Appearing

**Problem:** Edited law/question doesn't update

**Solutions:**
1. Hard refresh browser (Ctrl+F5)
2. Check for error messages
3. Verify file permissions
4. Restart application

### 404 Error on Admin Pages

**Problem:** `/admin/` routes return 404

**Solutions:**
1. Ensure `admin_helper.py` exists
2. Check `app.py` has admin routes
3. Verify templates exist in `templates/admin/`
4. Restart Flask server

### Flash Messages Not Showing

**Problem:** No success/error messages appear

**Solutions:**
1. Check Flask secret key is set
2. Clear browser cache
3. Check template includes flash messages block

---

## 📊 Statistics Explained

### Dashboard Metrics

**Total Laws:**
- Count of all `.txt` files in `laws/` directory
- Includes laws with and without metadata

**Quiz Questions:**
- Total approved questions in database
- Only counts `is_approved = 1`

**Laws with Metadata:**
- Laws that have English summary and keywords
- Required for AI search functionality

**Coverage:**
- Percentage of laws with complete metadata
- Formula: (Laws with metadata / Total laws) × 100%
- Target: 100% for best AI performance

**Questions by Category:**
- Breakdown of questions by category tag
- Categories: arrest, search, warrants, etc.
- Helps identify coverage gaps

**Questions by Difficulty:**
- Easy: Basic questions (simple facts)
- Medium: Moderate difficulty (understanding)
- Hard: Complex questions (analysis, application)
- Ideal distribution: 30% easy, 50% medium, 20% hard

---

## 🔄 Common Workflows

### Adding New Content

**Complete Workflow for New Law:**
1. Login to admin panel
2. Go to Laws → Add New Law
3. Enter filename (e.g., `new_law.txt`)
4. Paste Georgian law text
5. Write English summary (3-5 sentences)
6. Add English keywords (5-10 keywords)
7. Save law
8. Test on Browse page
9. Test AI chat with questions about the law

### Moderating Questions

**Daily Moderation Workflow:**
1. Login to admin panel
2. Go to Questions page
3. Review recent questions (sorted by ID desc)
4. For each question:
   - Read question text
   - Check all options make sense
   - Verify correct answer is accurate
   - Read explanation for clarity
   - Enable if good, edit if needs fixes
5. Disable or delete problematic questions

### Updating Law Content

**Law Update Workflow:**
1. Login to admin panel
2. Go to Laws → Find the law
3. Click Edit
4. Update Georgian text if law changed
5. Update English summary if needed
6. Update keywords for better search
7. Save changes
8. Test on law detail page
9. Test in quiz (if questions exist)

---

## 🚀 Advanced Tips

### Bulk Operations

To bulk-edit multiple laws/questions:
1. Use database scripts (SQLite for questions)
2. Edit files directly in `laws/` folder (backup first!)
3. Use CSV import/export (future feature)

### Content Strategy

**For Better Search:**
- Add comprehensive English keywords
- Include synonyms and related terms
- Use common search terms users might try

**For Better Quizzes:**
- Maintain balanced difficulty distribution
- Cover all major law topics
- Ensure questions are clear and unambiguous
- Write helpful explanations (not just answers)

### Performance Optimization

- Laws are loaded once at startup
- Changes require app restart (or use reload)
- Keep individual law files under 500KB
- Optimize large law texts for readability

---

## 📞 Support & Help

### Need Help?

1. **Check this guide** first
2. **Review error messages** carefully
3. **Check application logs** for details
4. **Test on local machine** before production

### Common Issues:

- **Login problems:** Check `.env` file
- **Layout broken:** Clear browser cache
- **Changes not saving:** Check file permissions
- **500 errors:** Check application logs

---

## 🔐 Production Deployment

### Before Going Live:

1. ✅ Change admin password in `.env`
2. ✅ Set `DEBUG=False` in `.env`
3. ✅ Use strong SECRET_KEY
4. ✅ Test all admin features
5. ✅ Backup database and laws
6. ✅ Set up HTTPS (SSL certificate)
7. ✅ Configure firewall rules
8. ✅ Monitor admin access logs

### Production `.env` Example:

```env
# Gemini API
GEMINI_API_KEY=your_actual_api_key

# Flask
SECRET_KEY=random_64_character_secret_key_here
DEBUG=False

# Admin (CHANGE THESE!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=VeryStrongPassword123!@#
```

---

## 📝 Summary

The admin panel provides:

✅ **Dashboard** - Statistics and quick actions
✅ **Law Management** - Add, edit, delete laws
✅ **Question Management** - Moderate quiz content
✅ **Security** - Password protection and sessions
✅ **User-Friendly** - Clean design, easy navigation
✅ **Responsive** - Works on all devices

**Access:** `http://YOUR_SITE/admin/login`
**Username:** `admin`
**Password:** `nexus2025!` (change this!)

---

Made with ❤️ for San Andreas Roleplay Server
