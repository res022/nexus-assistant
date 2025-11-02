# -*- coding: utf-8 -*-
"""
Nexus Assistant - Georgian Law Database with AI Assistant
Main Flask Application
"""

from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from law_parser import LawParser
from serverrules_parser import ServerRulesParser
from gemini_helper import GeminiHelper
from database import QuizDatabase
from config import Config
from admin_helper import check_admin_auth, login_required, get_admin_stats
from user_manager import UserManager, user_login_required
import os
from datetime import datetime
import uuid
import json
import codecs
import sqlite3

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialize components
law_parser = LawParser()
serverrules_parser = ServerRulesParser()
gemini_helper = GeminiHelper()
quiz_db = QuizDatabase()
user_manager = UserManager()

# Load all laws and server rules on startup
print("[INFO] Loading all law documents...")
law_parser.load_all_laws()
print(f"[INFO] Loaded {len(law_parser.laws)} laws successfully")

print("[INFO] Loading server rules...")
serverrules_parser.load_metadata()
serverrules_parser.parse_all_rules()
print(f"[INFO] Loaded {len(serverrules_parser.rules)} server rules successfully")

print(f"[INFO] Quiz questions available: {quiz_db.get_question_count()}")


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html', total_laws=len(law_parser.laws))


@app.route('/browse')
def browse():
    """Browse all laws page"""
    laws = law_parser.laws
    
    # Get search query if provided
    search_query = request.args.get('q', '').strip()
    
    if search_query:
        # Filter laws by search query (search in Georgian title or English summary/keywords)
        filtered_laws = []
        query_lower = search_query.lower()
        
        for law in laws:
            if (query_lower in law.law_name.lower() or 
                query_lower in law.summary_en.lower() or 
                query_lower in law.keywords_en.lower()):
                filtered_laws.append(law)
        
        laws = filtered_laws
    
    return render_template('browse.html', laws=laws, search_query=search_query)


@app.route('/law/<filename>')
def law_detail(filename):
    """View a single law in detail"""
    law = law_parser.get_law_by_filename(filename)
    
    if not law:
        return render_template('error.html', 
                             message=f"კანონი '{filename}' ვერ მოიძებნა"), 404
    
    return render_template('law_detail.html', law=law)


@app.route('/chat')
def chat():
    """AI chat assistant page"""
    # Initialize session conversation history if not exists
    if 'conversation_history' not in session:
        session['conversation_history'] = []
    
    return render_template('chat.html', 
                         conversation_history=session.get('conversation_history', []))


@app.route('/api/ask', methods=['POST'])
def api_ask():
    """
    API endpoint for asking questions to the AI assistant

    Request JSON:
    {
        "question": "Georgian question text",
        "source": "laws" or "rules" (optional, defaults to "laws")
    }

    Response JSON:
    {
        "answer": "Georgian answer text",
        "sources": ["Law 1", "Law 2"],
        "relevant_items": [{item details}],
        "error": false
    }
    """
    import sys
    try:
        print("[DEBUG] API ask called", flush=True)
        sys.stdout.flush()

        data = request.get_json()
        georgian_question = data.get('question', '').strip()
        source_type = data.get('source', 'laws').lower()  # 'laws' or 'rules'

        # Don't print Georgian text to console to avoid encoding errors
        print(f"[DEBUG] Question received (length: {len(georgian_question)} chars, source: {source_type})", flush=True)
        sys.stdout.flush()

        if not georgian_question:
            return jsonify({
                'error': True,
                'message': 'გთხოვთ შეიყვანოთ კითხვა'
            }), 400

        # Choose source based on user selection
        if source_type == 'rules':
            # Use server rules
            print(f"[INFO] Using AI to select relevant server rules...", flush=True)
            sys.stdout.flush()

            # Convert rules to law-like format for compatibility
            rules_as_laws = []
            for rule in serverrules_parser.rules:
                # Create a simple object with needed attributes
                class RuleAsLaw:
                    def __init__(self, rule_data):
                        self.filename = rule_data['filename']
                        self.law_name = rule_data['title']
                        self.content = rule_data['content']
                        self.georgian_text = rule_data['content']  # Same as content
                        self.summary_en = rule_data.get('summary_en', '')
                        self.keywords_en = rule_data.get('keywords_en', '')

                rules_as_laws.append(RuleAsLaw(rule))

            relevant_items = gemini_helper.select_relevant_laws(
                georgian_question,
                rules_as_laws,
                max_laws=Config.MAX_LAWS_TO_SEND
            )

            print(f"[INFO] Selected {len(relevant_items)} relevant rules", flush=True)
        else:
            # Use laws (default)
            print(f"[INFO] Using AI to select relevant laws...", flush=True)
            sys.stdout.flush()

            relevant_items = gemini_helper.select_relevant_laws(
                georgian_question,
                law_parser.laws,
                max_laws=Config.MAX_LAWS_TO_SEND
            )

            print(f"[INFO] Selected {len(relevant_items)} relevant laws", flush=True)

        sys.stdout.flush()

        # Step 3: Send to Gemini for answer generation
        print("[DEBUG] Calling Gemini API...", flush=True)
        sys.stdout.flush()

        # Update the context to indicate whether we're answering about laws or rules
        context_prefix = "სერვერის წესები" if source_type == 'rules' else "საქართველოს კანონები"
        result = gemini_helper.answer_question(georgian_question, relevant_items, context=context_prefix)

        print(f"[DEBUG] Gemini result error={result.get('error')}", flush=True)
        sys.stdout.flush()

        # Step 4: Add to conversation history
        if 'conversation_history' not in session:
            session['conversation_history'] = []

        session['conversation_history'].append({
            'question': georgian_question,
            'answer': result['answer'],
            'sources': result['sources'],
            'source_type': source_type,
            'timestamp': datetime.now().strftime('%H:%M')
        })
        session.modified = True

        # Prepare response with item details
        relevant_items_data = [
            {
                'filename': item.filename,
                'law_name': item.law_name,
                'summary_en': item.summary_en
            }
            for item in relevant_items
        ]

        return jsonify({
            'answer': result['answer'],
            'sources': result['sources'],
            'relevant_items': relevant_items_data,
            'source_type': source_type,
            'error': result.get('error', False)
        })

    except Exception as e:
        print(f"[ERROR] API ask failed: {str(e)}", flush=True)
        import traceback
        traceback.print_exc()
        sys.stdout.flush()
        return jsonify({
            'error': True,
            'message': f'შეცდომა: {str(e)}'
        }), 500


@app.route('/api/clear-history', methods=['POST'])
def api_clear_history():
    """Clear conversation history"""
    session['conversation_history'] = []
    session.modified = True
    return jsonify({'success': True})


@app.route('/api/laws')
def api_laws():
    """API endpoint to get all laws as JSON"""
    laws_data = [law.to_dict() for law in law_parser.laws]
    return jsonify({'laws': laws_data, 'total': len(laws_data)})


@app.route('/api/search')
def api_search():
    """API endpoint for searching laws by keywords"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    
    # Use English keyword search
    keywords = [query]
    results = law_parser.search_by_english_keywords(keywords, max_results=10)
    
    results_data = [
        {
            'filename': law.filename,
            'law_name': law.law_name,
            'summary_en': law.summary_en,
            'keywords_en': law.keywords_en
        }
        for law in results
    ]
    
    return jsonify({'results': results_data, 'total': len(results_data)})


@app.route('/quiz')
def quiz():
    """Quiz mode page"""
    # Initialize session ID if not exists
    if 'quiz_session_id' not in session:
        session['quiz_session_id'] = str(uuid.uuid4())

    # Get stats
    stats = quiz_db.get_user_stats(session['quiz_session_id'])
    question_count = quiz_db.get_question_count()

    return render_template('quiz.html', stats=stats, question_count=question_count)


@app.route('/api/quiz/start', methods=['POST'])
def api_quiz_start():
    """Start a new quiz session"""
    try:
        # Clear any existing quiz session to prevent caching issues
        if 'current_quiz' in session:
            session.pop('current_quiz')

        data = request.get_json() or {}
        num_questions = data.get('num_questions', 10)
        source_type = data.get('source_type', 'laws')  # Get source type from request (laws or rules)

        # Get random questions from specified source
        questions = quiz_db.get_random_questions(limit=num_questions, source_type=source_type)

        print(f"[DEBUG] Quiz start: source_type={source_type}, num_questions={num_questions}")
        print(f"[DEBUG] Got {len(questions)} questions from database")
        if questions:
            print(f"[DEBUG] First question ID: {questions[0]['id']}, source: {questions[0].get('source_type', 'N/A')}")
            print(f"[DEBUG] All question sources: {[q.get('source_type', 'N/A') for q in questions]}")
            print(f"[DEBUG] Question IDs: {[q['id'] for q in questions]}")

        if not questions:
            return jsonify({
                'error': True,
                'message': 'კითხვები ჯერ არ არის გენერირებული. გაუშვით quiz_generator.py'
            }), 400

        # If user is logged in, start a user quiz session
        user_quiz_session_id = None
        if session.get('user_id'):
            user_quiz_session_id = user_manager.start_quiz_session(session['user_id'])
            print(f"[DEBUG] Started user quiz session: {user_quiz_session_id}")

        # Store only question IDs in session (to keep session cookie small)
        session['current_quiz'] = {
            'question_ids': [q['id'] for q in questions],
            'current_index': 0,
            'start_time': datetime.now().isoformat(),
            'correct_count': 0,
            'user_session_id': user_quiz_session_id
        }
        session.modified = True

        print(f"[DEBUG] Stored {len(questions)} question IDs in session")
        print(f"[DEBUG] Session size check - IDs: {session['current_quiz']['question_ids']}")

        # Return full first question to frontend
        return jsonify({
            'success': True,
            'total_questions': len(questions),
            'first_question': questions[0]
        })

    except Exception as e:
        print(f"[ERROR] Quiz start failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': True,
            'message': f'შეცდომა: {str(e)}'
        }), 500


@app.route('/api/quiz/answer', methods=['POST'])
def api_quiz_answer():
    """Submit answer to current question"""
    try:
        if 'current_quiz' not in session:
            print("[ERROR] No current_quiz in session")
            return jsonify({'error': True, 'message': 'კითხვა ვერ მოიძებნა'}), 400

        data = request.get_json()
        question_id = data.get('question_id')
        user_answer = data.get('answer')

        print(f"[DEBUG] Received question_id: {question_id}, type: {type(question_id)}")
        print(f"[DEBUG] User answer received (length: {len(user_answer)} chars)")

        # Get full question details from database
        import sqlite3
        conn = sqlite3.connect(quiz_db.db_path)
        cursor = conn.cursor()

        # First check all IDs in database
        cursor.execute('SELECT id FROM quiz_questions WHERE is_approved = 1 LIMIT 10')
        all_ids = cursor.fetchall()
        print(f"[DEBUG] Sample question IDs in database: {[row[0] for row in all_ids]}")

        cursor.execute('''
            SELECT correct_answer, explanation, law_reference
            FROM quiz_questions
            WHERE id = ?
        ''', (question_id,))

        result = cursor.fetchone()

        if not result:
            conn.close()
            print(f"[ERROR] Question {question_id} not found in database")
            print(f"[ERROR] Session has questions with IDs: {[q['id'] for q in session['current_quiz']['questions']]}")
            return jsonify({'error': True, 'message': f'კითხვა {question_id} ვერ მოიძებნა'}), 404

        correct_answer, explanation, law_reference = result
        conn.close()
        is_correct = (user_answer == correct_answer)

        # Record answer for logged-in users
        if session.get('user_id'):
            user_session_id = session['current_quiz'].get('user_session_id')
            user_manager.record_quiz_answer(
                session['user_id'],
                user_session_id,
                question_id,
                user_answer,
                is_correct
            )
            print(f"[DEBUG] Recorded answer for user {session['user_id']}")

        # Also record for session-based stats (for non-logged-in users)
        if not session.get('user_id'):
            quiz_db.record_answer(
                session['quiz_session_id'],
                question_id,
                user_answer,
                is_correct
            )

        # Update correct count
        quiz = session['current_quiz']
        if is_correct:
            quiz['correct_count'] = quiz.get('correct_count', 0) + 1

        # Move to next question
        quiz['current_index'] += 1
        session.modified = True

        # Check if quiz is complete
        total_questions = len(quiz['question_ids'])
        if quiz['current_index'] >= total_questions:
            # Complete user quiz session if logged in
            if session.get('user_id') and quiz.get('user_session_id'):
                user_manager.complete_quiz_session(
                    quiz['user_session_id'],
                    total_questions,
                    quiz.get('correct_count', 0)
                )
                print(f"[DEBUG] Completed user quiz session")

            next_question = None
            is_complete = True
        else:
            # Fetch next question from database
            next_question_id = quiz['question_ids'][quiz['current_index']]

            # Get specific question by ID
            conn = sqlite3.connect(quiz_db.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, question_text, options, category, difficulty
                FROM quiz_questions
                WHERE id = ?
            ''', (next_question_id,))
            next_row = cursor.fetchone()
            conn.close()

            if next_row:
                import json
                next_question = {
                    'id': next_row[0],
                    'question': next_row[1],
                    'options': json.loads(next_row[2]),
                    'category': next_row[3],
                    'difficulty': next_row[4]
                }
            else:
                next_question = None
            is_complete = False

        print(f"[DEBUG] Quiz progress: {quiz['current_index']}/{total_questions}")

        # Security: Always send explanation for learning, but only send correct_answer when wrong
        # This prevents users from inspecting element to see answers before submitting
        response_data = {
            'is_correct': is_correct,
            'user_answer': user_answer,
            'next_question': next_question,
            'is_complete': is_complete,
            'current_index': quiz['current_index'],
            'total_questions': total_questions,
            'explanation': explanation,  # Always send for learning
            'law_reference': law_reference  # Always send for context
        }

        # Only include correct_answer if answered incorrectly (to prevent cheating)
        if not is_correct:
            response_data['correct_answer'] = correct_answer

        return jsonify(response_data)

    except Exception as e:
        print(f"[ERROR] Quiz answer failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': True,
            'message': f'შეცდომა: {str(e)}'
        }), 500


@app.route('/api/quiz/stats')
def api_quiz_stats():
    """Get user's quiz statistics"""
    if 'quiz_session_id' not in session:
        return jsonify({'error': True, 'message': 'სესია ვერ მოიძებნა'}), 400

    stats = quiz_db.get_user_stats(session['quiz_session_id'])
    return jsonify(stats)


# ============================================================================
# USER ACCOUNT ROUTES
# ============================================================================

@app.route('/register', methods=['GET', 'POST'])
def user_register():
    """User registration page"""
    if session.get('user_id'):
        return redirect(url_for('user_dashboard'))

    # Get the next URL from query parameter
    next_url = request.args.get('next')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        display_name = request.form.get('display_name', '').strip()

        # Validation
        if not username or len(username) < 3:
            flash('მომხმარებლის სახელი უნდა იყოს მინიმუმ 3 სიმბოლო', 'error')
        elif email and '@' not in email:
            flash('არასწორი ელ. ფოსტა', 'error')
        elif not password or len(password) < 6:
            flash('პაროლი უნდა იყოს მინიმუმ 6 სიმბოლო', 'error')
        elif password != confirm_password:
            flash('პაროლები არ ემთხვევა', 'error')
        else:
            result = user_manager.create_user(username, email, password, display_name)

            if result['success']:
                flash('ანგარიში წარმატებით შეიქმნა! გთხოვთ შეხვიდეთ', 'success')
                # Pass next URL to login page
                if next_url:
                    return redirect(url_for('user_login', next=next_url))
                return redirect(url_for('user_login'))
            else:
                flash(result['error'], 'error')

    return render_template('user/register.html', next=next_url)


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    """User login page"""
    if session.get('user_id'):
        return redirect(url_for('user_dashboard'))

    # Get the next URL from query parameter
    next_url = request.args.get('next') or request.form.get('next')

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        if not username or not password:
            flash('Username and password are required', 'error')
        else:
            result = user_manager.authenticate_user(username, password)

            if result['success']:
                user = result['user']
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['display_name'] = user['display_name']

                flash(f'Welcome back, {user["display_name"]}!', 'success')

                # Redirect to the original URL if it exists, otherwise dashboard
                if next_url:
                    return redirect(next_url)
                return redirect(url_for('user_dashboard'))
            else:
                flash(result['error'], 'error')

    return render_template('user/login.html', next=next_url)


@app.route('/logout')
def user_logout():
    """User logout"""
    session.pop('user_id', None)
    session.pop('username', None)
    session.pop('display_name', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))


@app.route('/dashboard')
@user_login_required
def user_dashboard():
    """User dashboard with statistics"""
    user_id = session.get('user_id')
    user_info = user_manager.get_user_by_id(user_id)
    stats = user_manager.get_user_stats(user_id)

    return render_template('user/dashboard.html', user=user_info, stats=stats)


@app.route('/profile')
@user_login_required
def user_profile():
    """User profile page"""
    user_id = session.get('user_id')
    user_info = user_manager.get_user_by_id(user_id)

    return render_template('user/profile.html', user=user_info)


@app.route('/leaderboard')
def leaderboard():
    """Public leaderboard"""
    leaders = user_manager.get_leaderboard(limit=20)
    return render_template('user/leaderboard.html', leaders=leaders)


# ============================================================================
# ADMIN PANEL ROUTES
# ============================================================================

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if check_admin_auth(username, password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Successfully logged in!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials', 'error')

    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    flash('Logged out successfully', 'success')
    return redirect(url_for('admin_login'))


@app.route('/admin')
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    """Admin dashboard"""
    stats = get_admin_stats(law_parser, quiz_db)
    return render_template('admin/dashboard.html', stats=stats)


@app.route('/admin/laws')
@login_required
def admin_laws():
    """Manage laws"""
    laws = law_parser.laws
    return render_template('admin/laws.html', laws=laws)


@app.route('/admin/laws/add', methods=['GET', 'POST'])
@login_required
def admin_add_law():
    """Add new law"""
    if request.method == 'POST':
        try:
            filename = request.form.get('filename')
            law_name = request.form.get('law_name')
            content = request.form.get('content')
            summary_en = request.form.get('summary_en')
            keywords_en = request.form.get('keywords_en')

            # Create law file
            law_path = os.path.join(Config.LAWS_DIRECTORY, filename)

            with codecs.open(law_path, 'w', encoding='utf-8') as f:
                f.write(f"{law_name}\n")
                f.write(f"{content}\n\n")
                f.write(f"{Config.METADATA_SEPARATOR}\n")
                f.write(f"SUMMARY_EN: {summary_en}\n")
                f.write(f"KEYWORDS_EN: {keywords_en}\n")

            # Reload laws
            law_parser.load_all_laws()

            flash(f'Law "{law_name}" added successfully!', 'success')
            return redirect(url_for('admin_laws'))

        except Exception as e:
            flash(f'Error adding law: {str(e)}', 'error')

    return render_template('admin/law_form.html', law=None)


@app.route('/admin/laws/edit/<filename>', methods=['GET', 'POST'])
@login_required
def admin_edit_law(filename):
    """Edit existing law"""
    law = law_parser.get_law_by_filename(filename)

    if not law:
        flash('Law not found', 'error')
        return redirect(url_for('admin_laws'))

    if request.method == 'POST':
        try:
            law_name = request.form.get('law_name')
            content = request.form.get('content')
            summary_en = request.form.get('summary_en')
            keywords_en = request.form.get('keywords_en')

            # Update law file
            law_path = os.path.join(Config.LAWS_DIRECTORY, filename)

            with codecs.open(law_path, 'w', encoding='utf-8') as f:
                f.write(f"{law_name}\n")
                f.write(f"{content}\n\n")
                f.write(f"{Config.METADATA_SEPARATOR}\n")
                f.write(f"SUMMARY_EN: {summary_en}\n")
                f.write(f"KEYWORDS_EN: {keywords_en}\n")

            # Reload laws
            law_parser.load_all_laws()

            flash(f'Law "{law_name}" updated successfully!', 'success')
            return redirect(url_for('admin_laws'))

        except Exception as e:
            flash(f'Error updating law: {str(e)}', 'error')

    return render_template('admin/law_form.html', law=law)


@app.route('/admin/laws/delete/<filename>', methods=['POST'])
@login_required
def admin_delete_law(filename):
    """Delete a law"""
    try:
        law_path = os.path.join(Config.LAWS_DIRECTORY, filename)

        if os.path.exists(law_path):
            os.remove(law_path)
            law_parser.load_all_laws()
            flash('Law deleted successfully!', 'success')
        else:
            flash('Law file not found', 'error')

    except Exception as e:
        flash(f'Error deleting law: {str(e)}', 'error')

    return redirect(url_for('admin_laws'))


@app.route('/admin/questions')
@login_required
def admin_questions():
    """Manage quiz questions"""
    import sqlite3

    conn = sqlite3.connect(quiz_db.db_path)
    cursor = conn.cursor()

    page = request.args.get('page', 1, type=int)
    per_page = 50
    offset = (page - 1) * per_page

    cursor.execute('''
        SELECT id, question_text, category, difficulty, is_approved, law_reference
        FROM quiz_questions
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    ''', (per_page, offset))

    questions = []
    for row in cursor.fetchall():
        questions.append({
            'id': row[0],
            'question_text': row[1],
            'category': row[2],
            'difficulty': row[3],
            'is_approved': row[4],
            'law_reference': row[5]
        })

    cursor.execute('SELECT COUNT(*) FROM quiz_questions')
    total_questions = cursor.fetchone()[0]

    conn.close()

    total_pages = (total_questions + per_page - 1) // per_page

    return render_template('admin/questions.html',
                         questions=questions,
                         page=page,
                         total_pages=total_pages,
                         total_questions=total_questions)


@app.route('/admin/questions/edit/<int:question_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_question(question_id):
    """Edit a quiz question"""
    import sqlite3

    conn = sqlite3.connect(quiz_db.db_path)
    cursor = conn.cursor()

    if request.method == 'POST':
        try:
            question_text = request.form.get('question_text')
            options = json.dumps({
                'A': request.form.get('option_a'),
                'B': request.form.get('option_b'),
                'C': request.form.get('option_c'),
                'D': request.form.get('option_d')
            })
            correct_answer = request.form.get('correct_answer')
            explanation = request.form.get('explanation')
            category = request.form.get('category')
            difficulty = request.form.get('difficulty')

            cursor.execute('''
                UPDATE quiz_questions
                SET question_text = ?, options = ?, correct_answer = ?,
                    explanation = ?, category = ?, difficulty = ?
                WHERE id = ?
            ''', (question_text, options, correct_answer, explanation,
                  category, difficulty, question_id))

            conn.commit()
            conn.close()

            flash('Question updated successfully!', 'success')
            return redirect(url_for('admin_questions'))

        except Exception as e:
            conn.close()
            flash(f'Error updating question: {str(e)}', 'error')

    cursor.execute('''
        SELECT question_text, options, correct_answer, explanation,
               category, difficulty, law_reference
        FROM quiz_questions
        WHERE id = ?
    ''', (question_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        flash('Question not found', 'error')
        return redirect(url_for('admin_questions'))

    question = {
        'id': question_id,
        'question_text': row[0],
        'options': json.loads(row[1]),
        'correct_answer': row[2],
        'explanation': row[3],
        'category': row[4],
        'difficulty': row[5],
        'law_reference': row[6]
    }

    return render_template('admin/question_form.html', question=question)


@app.route('/admin/questions/delete/<int:question_id>', methods=['POST'])
@login_required
def admin_delete_question(question_id):
    """Delete a quiz question"""
    import sqlite3

    try:
        conn = sqlite3.connect(quiz_db.db_path)
        cursor = conn.cursor()

        cursor.execute('DELETE FROM quiz_questions WHERE id = ?', (question_id,))
        conn.commit()
        conn.close()

        flash('Question deleted successfully!', 'success')

    except Exception as e:
        flash(f'Error deleting question: {str(e)}', 'error')

    return redirect(url_for('admin_questions'))


@app.route('/admin/questions/toggle/<int:question_id>', methods=['POST'])
@login_required
def admin_toggle_question(question_id):
    """Toggle question approval status"""
    import sqlite3

    try:
        conn = sqlite3.connect(quiz_db.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE quiz_questions
            SET is_approved = NOT is_approved
            WHERE id = ?
        ''', (question_id,))

        conn.commit()
        conn.close()

        flash('Question status updated!', 'success')

    except Exception as e:
        flash(f'Error updating question: {str(e)}', 'error')

    return redirect(url_for('admin_questions'))


# ============================================================================
# SHARED QUIZ SYSTEM
# ============================================================================

@app.route('/admin/quizzes')
@login_required
def admin_quizzes():
    """Admin page to manage shared quizzes"""
    quizzes = quiz_db.get_all_shared_quizzes()

    # Add question count to each quiz
    for quiz in quizzes:
        question_ids = json.loads(quiz['question_ids']) if isinstance(quiz['question_ids'], str) else quiz['question_ids']
        quiz['question_count'] = len(question_ids)

    total_quizzes = len(quizzes)
    active_quizzes = len([q for q in quizzes if q['is_active']])
    total_attempts = sum(q['attempt_count'] for q in quizzes)

    # Count unique users across all quizzes
    conn = sqlite3.connect(quiz_db.db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(DISTINCT user_id) FROM shared_quiz_attempts')
    unique_users = cursor.fetchone()[0]
    conn.close()

    return render_template('admin/quizzes.html',
                         quizzes=quizzes,
                         total_quizzes=total_quizzes,
                         active_quizzes=active_quizzes,
                         total_attempts=total_attempts,
                         unique_users=unique_users)


@app.route('/admin/quiz/create')
@login_required
def admin_quiz_create():
    """Admin page to create shared quiz"""
    return render_template('admin/create_quiz.html')


@app.route('/admin/api/questions')
@login_required
def admin_api_questions():
    """API to get questions for quiz creation"""
    source = request.args.get('source', 'laws')
    difficulty = request.args.get('difficulty', '')

    conn = sqlite3.connect(quiz_db.db_path)
    cursor = conn.cursor()

    query = '''
        SELECT id, question_text, options, correct_answer, explanation,
               law_reference, category, difficulty, source_type
        FROM quiz_questions
        WHERE is_approved = 1 AND source_type = ?
    '''
    params = [source]

    if difficulty:
        query += ' AND difficulty = ?'
        params.append(difficulty)

    query += ' ORDER BY id DESC LIMIT 500'

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    questions = []
    for row in rows:
        questions.append({
            'id': row[0],
            'question_text': row[1],
            'options': json.loads(row[2]),
            'correct_answer': row[3],
            'explanation': row[4],
            'law_reference': row[5],
            'category': row[6],
            'difficulty': row[7],
            'source_type': row[8]
        })

    return jsonify({'questions': questions})


@app.route('/admin/api/quiz/create', methods=['POST'])
@login_required
def admin_api_quiz_create():
    """API to create a new shared quiz"""
    try:
        data = request.get_json()
        title = data.get('title')
        description = data.get('description', '')
        questions = data.get('questions', [])

        if not title or len(questions) == 0:
            return jsonify({'success': False, 'message': 'Title and questions are required'}), 400

        # Generate unique quiz ID
        import uuid
        quiz_id = str(uuid.uuid4())

        # Separate existing and custom questions
        existing_question_ids = []
        custom_questions_to_add = []

        for q in questions:
            if q.get('is_custom'):
                # This is a custom question, add it to database first
                question_data = {
                    'question': q['question_text'],
                    'options': q['options'],
                    'correct_answer': q['correct_answer'],
                    'explanation': q['explanation'],
                    'law_reference': q['law_reference'],
                    'category': q['category'],
                    'difficulty': q['difficulty'],
                    'source_type': q['source_type']
                }
                new_id = quiz_db.add_question(question_data)
                existing_question_ids.append(new_id)
            else:
                # Existing question from database
                existing_question_ids.append(q['id'])

        # Create shared quiz
        quiz_db.create_shared_quiz(
            quiz_id=quiz_id,
            title=title,
            description=description,
            question_ids=existing_question_ids,
            admin_username=session.get('username')
        )

        quiz_url = f"{request.host_url}quiz/shared/{quiz_id}"

        return jsonify({
            'success': True,
            'quiz_id': quiz_id,
            'quiz_url': quiz_url
        })

    except Exception as e:
        print(f"[ERROR] Quiz creation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/api/quiz/toggle', methods=['POST'])
@login_required
def admin_api_quiz_toggle():
    """API to toggle quiz active status"""
    try:
        data = request.get_json()
        quiz_id = data.get('quiz_id')

        quiz_db.toggle_quiz_active(quiz_id)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/quiz/<quiz_id>/results')
@login_required
def admin_quiz_results(quiz_id):
    """Admin page to view quiz results"""
    quiz = quiz_db.get_shared_quiz(quiz_id)

    if not quiz:
        flash('Quiz not found', 'error')
        return redirect(url_for('admin_quizzes'))

    attempts = quiz_db.get_quiz_attempts(quiz_id)

    # Calculate statistics
    unique_users = len(set(a['user_id'] for a in attempts))
    question_count = len(quiz['question_ids'])

    if attempts:
        total_score = sum(a['score'] for a in attempts)
        total_possible = sum(a['total_questions'] for a in attempts)
        average_score = (total_score / total_possible * 100) if total_possible > 0 else 0

        passed = sum(1 for a in attempts if (a['score'] / a['total_questions'] * 100) >= 60)
        pass_rate = int((passed / len(attempts) * 100)) if attempts else 0
    else:
        average_score = 0
        pass_rate = 0

    return render_template('admin/quiz_results.html',
                         quiz=quiz,
                         attempts=attempts,
                         unique_users=unique_users,
                         question_count=question_count,
                         average_score=average_score,
                         pass_rate=pass_rate)


@app.route('/admin/api/quiz/allow-retake', methods=['POST'])
@login_required
def admin_api_allow_retake():
    """API to allow a user to retake a quiz"""
    try:
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        user_id = data.get('user_id')

        success = quiz_db.allow_retake(quiz_id, user_id)

        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Attempt not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/admin/api/quiz/attempt/<int:attempt_id>')
@login_required
def admin_api_quiz_attempt(attempt_id):
    """API to get detailed attempt information"""
    try:
        conn = sqlite3.connect(quiz_db.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM shared_quiz_attempts WHERE id = ?
        ''', (attempt_id,))

        attempt = cursor.fetchone()
        conn.close()

        if attempt:
            return jsonify({
                'success': True,
                'attempt': dict(attempt)
            })
        else:
            return jsonify({'success': False, 'message': 'Attempt not found'}), 404

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/quiz/shared/<quiz_id>')
def shared_quiz(quiz_id):
    """Public page to take a shared quiz"""
    # Check if user is logged in
    if not session.get('user_id'):
        flash('გთხოვთ შეხვიდეთ სისტემაში ქვიზის გასავლელად', 'error')
        return redirect(url_for('user_login', next=request.url))

    quiz = quiz_db.get_shared_quiz(quiz_id)

    if not quiz:
        flash('ქვიზი ვერ მოიძებნა', 'error')
        return redirect(url_for('index'))

    if not quiz['is_active']:
        flash('ეს ქვიზი არ არის აქტიური', 'error')
        return redirect(url_for('index'))

    # Check if user already attempted this quiz
    user_attempt = quiz_db.check_user_attempt(quiz_id, session['user_id'])

    if user_attempt['has_attempted'] and not user_attempt['can_retake']:
        # Don't send score to user - only completion date
        # Admin can see scores in the admin panel
        return render_template('quiz_already_attempted.html',
                             completed_at=user_attempt.get('completed_at', 'N/A'))

    # Get questions for the quiz
    questions = quiz_db.get_shared_quiz_questions(quiz_id)

    if not questions:
        flash('კითხვები ვერ მოიძებნა', 'error')
        return redirect(url_for('index'))

    return render_template('shared_quiz.html',
                         quiz=quiz,
                         questions=questions,
                         questions_json=json.dumps(questions))


@app.route('/api/quiz/shared/submit', methods=['POST'])
@user_login_required
def api_shared_quiz_submit():
    """API to submit shared quiz answers"""
    try:
        if not session.get('user_id'):
            return jsonify({'success': False, 'message': 'Not logged in'}), 401

        data = request.get_json()
        quiz_id = data.get('quiz_id')
        answers = data.get('answers', [])
        score = data.get('score', 0)
        total_questions = data.get('total_questions', 0)

        # Check if user already attempted (double-check)
        user_attempt = quiz_db.check_user_attempt(quiz_id, session['user_id'])
        if user_attempt['has_attempted'] and not user_attempt['can_retake']:
            return jsonify({'success': False, 'message': 'Already attempted'}), 400

        # Record attempt - returns True if successful, False if failed
        success = quiz_db.record_shared_quiz_attempt(
            quiz_id=quiz_id,
            user_id=session['user_id'],
            score=score,
            total_questions=total_questions,
            answers=answers
        )

        if not success:
            return jsonify({'success': False, 'message': 'Failed to record attempt. You may not have permission to retake this quiz.'}), 403

        return jsonify({'success': True})

    except Exception as e:
        print(f"[ERROR] Shared quiz submission failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================================================
# MULTIPLAYER ROUTES
# ============================================================================

# Add custom Jinja filter for JSON parsing
@app.template_filter('from_json')
def from_json_filter(s):
    """Parse JSON string in templates"""
    try:
        return json.loads(s)
    except:
        return []

@app.route('/multiplayer')
@user_login_required
def multiplayer_lobby():
    """Multiplayer lobby page"""
    return render_template('multiplayer_lobby.html')

@app.route('/api/multiplayer/create', methods=['POST'])
@user_login_required
def api_create_match():
    """API to create multiplayer match"""
    try:
        data = request.get_json()
        num_questions = data.get('num_questions', 10)
        difficulty = data.get('difficulty')
        source_type = data.get('source_type', 'laws')

        match_id = quiz_db.create_multiplayer_match(
            creator_id=session['user_id'],
            num_questions=num_questions,
            difficulty=difficulty,
            source_type=source_type
        )

        return jsonify({'success': True, 'match_id': match_id})

    except Exception as e:
        print(f"[ERROR] Create match failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/multiplayer/join', methods=['POST'])
@user_login_required
def api_join_match():
    """API to join multiplayer match"""
    try:
        data = request.get_json()
        match_id = data.get('match_id')

        result = quiz_db.join_multiplayer_match(match_id, session['user_id'])
        return jsonify(result)

    except Exception as e:
        print(f"[ERROR] Join match failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/multiplayer/waiting')
@user_login_required
def api_waiting_matches():
    """API to get waiting matches"""
    try:
        matches = quiz_db.get_waiting_matches()
        return jsonify({'matches': matches})

    except Exception as e:
        print(f"[ERROR] Get waiting matches failed: {str(e)}")
        return jsonify({'matches': []}), 500

@app.route('/api/multiplayer/my-matches')
@user_login_required
def api_my_matches():
    """API to get user's recent matches"""
    try:
        matches = quiz_db.get_user_matches(session['user_id'])
        return jsonify({'matches': matches})

    except Exception as e:
        print(f"[ERROR] Get user matches failed: {str(e)}")
        return jsonify({'matches': []}), 500

@app.route('/multiplayer/match/<match_id>')
@user_login_required
def multiplayer_match(match_id):
    """Multiplayer match page"""
    match = quiz_db.get_multiplayer_match(match_id)

    if not match:
        flash('მატჩი ვერ მოიძებნა', 'error')
        return redirect(url_for('multiplayer_lobby'))

    # Check if user is part of this match
    if match['creator_id'] != session['user_id'] and match.get('opponent_id') != session['user_id']:
        # If waiting and not creator, try to join
        if match['status'] == 'waiting':
            result = quiz_db.join_multiplayer_match(match_id, session['user_id'])
            if not result['success']:
                flash(result['message'], 'error')
                return redirect(url_for('multiplayer_lobby'))
            match = quiz_db.get_multiplayer_match(match_id)
        else:
            flash('თქვენ არ ხართ ამ მატჩის წევრი', 'error')
            return redirect(url_for('multiplayer_lobby'))

    # Get questions
    questions = quiz_db.get_match_questions(match_id)

    # Get user info
    current_user = user_manager.get_user_by_id(session['user_id'])

    # Determine opponent (the other player)
    opponent = None
    if match.get('opponent_id'):
        # If current user is creator, opponent is the opponent_id
        # If current user is opponent, opponent is the creator
        if session['user_id'] == match['creator_id']:
            opponent = user_manager.get_user_by_id(match['opponent_id'])
        else:
            opponent = user_manager.get_user_by_id(match['creator_id'])

    share_url = request.host_url + f"multiplayer/match/{match_id}"

    return render_template('multiplayer_match.html',
                         match=match,
                         questions=questions,
                         questions_json=json.dumps(questions),
                         current_user_name=current_user['display_name'],
                         opponent_name=opponent['display_name'] if opponent else None,
                         share_url=share_url)

@app.route('/api/multiplayer/status/<match_id>')
@user_login_required
def api_match_status(match_id):
    """API to check match status"""
    try:
        match = quiz_db.get_multiplayer_match(match_id)
        if not match:
            return jsonify({'error': 'Match not found'}), 404

        return jsonify({'status': match['status']})

    except Exception as e:
        print(f"[ERROR] Get match status failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/multiplayer/submit', methods=['POST'])
@user_login_required
def api_submit_multiplayer():
    """API to submit multiplayer results"""
    try:
        data = request.get_json()
        match_id = data.get('match_id')
        answers = data.get('answers', [])
        times = data.get('times', [])
        score = data.get('score', 0)

        quiz_db.submit_multiplayer_result(match_id, session['user_id'], answers, times, score)

        return jsonify({'success': True})

    except Exception as e:
        print(f"[ERROR] Submit multiplayer result failed: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/multiplayer/check-results/<match_id>')
@user_login_required
def api_check_results(match_id):
    """API to check if both players finished"""
    try:
        match = quiz_db.get_multiplayer_match(match_id)
        if not match:
            return jsonify({'error': 'Match not found'}), 404

        both_finished = match['status'] == 'completed'

        return jsonify({'both_finished': both_finished})

    except Exception as e:
        print(f"[ERROR] Check results failed: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/multiplayer/results/<match_id>')
@user_login_required
def multiplayer_results(match_id):
    """Multiplayer results page"""
    match = quiz_db.get_multiplayer_match(match_id)

    if not match:
        flash('მატჩი ვერ მოიძებნა', 'error')
        return redirect(url_for('multiplayer_lobby'))

    # Check if user is part of this match
    if match['creator_id'] != session['user_id'] and match.get('opponent_id') != session['user_id']:
        flash('თქვენ არ ხართ ამ მატჩის წევრი', 'error')
        return redirect(url_for('multiplayer_lobby'))

    # Get results
    results = quiz_db.get_multiplayer_results(match_id)
    questions = quiz_db.get_match_questions(match_id)

    return render_template('multiplayer_results.html',
                         match=match,
                         results=results,
                         questions=questions)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('error.html',
                         message="გვერდი ვერ მოიძებნა"), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('error.html', 
                         message="სერვერის შიდა შეცდომა"), 500


if __name__ == '__main__':
    print("\n" + "="*60)
    print("   Nexus Assistant - Georgian Law Database")
    print("="*60)
    print(f"   Total Laws Loaded: {len(law_parser.laws)}")
    print(f"   Gemini API Status: {'OK - Configured' if gemini_helper.model else 'ERROR - Not Configured'}")
    print("="*60)
    print("\n   Starting Flask server...")
    print("   Open http://localhost:5000 in your browser\n")
    
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5000)
