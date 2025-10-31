# -*- coding: utf-8 -*-
"""
Nexus Assistant - Georgian Law Database with AI Assistant
Main Flask Application
"""

from flask import Flask, render_template, request, jsonify, session
from law_parser import LawParser
from gemini_helper import GeminiHelper
from database import QuizDatabase
from config import Config
import os
from datetime import datetime
import uuid

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Initialize components
law_parser = LawParser()
gemini_helper = GeminiHelper()
quiz_db = QuizDatabase()

# Load all laws on startup
print("[INFO] Loading all law documents...")
law_parser.load_all_laws()
print(f"[INFO] Loaded {len(law_parser.laws)} laws successfully")
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
        "question": "Georgian question text"
    }

    Response JSON:
    {
        "answer": "Georgian answer text",
        "sources": ["Law 1", "Law 2"],
        "relevant_laws": [{law details}],
        "error": false
    }
    """
    import sys
    try:
        print("[DEBUG] API ask called", flush=True)
        sys.stdout.flush()

        data = request.get_json()
        georgian_question = data.get('question', '').strip()

        # Don't print Georgian text to console to avoid encoding errors
        print(f"[DEBUG] Question received (length: {len(georgian_question)} chars)", flush=True)
        sys.stdout.flush()

        if not georgian_question:
            return jsonify({
                'error': True,
                'message': 'გთხოვთ შეიყვანოთ კითხვა'
            }), 400

        # Use Gemini AI to intelligently select the most relevant laws
        print(f"[INFO] Using AI to select relevant laws...", flush=True)
        sys.stdout.flush()

        relevant_laws = gemini_helper.select_relevant_laws(
            georgian_question,
            law_parser.laws,
            max_laws=Config.MAX_LAWS_TO_SEND
        )

        print(f"[INFO] Selected {len(relevant_laws)} relevant laws", flush=True)
        sys.stdout.flush()

        # Step 3: Send to Gemini for answer generation
        print("[DEBUG] Calling Gemini API...", flush=True)
        sys.stdout.flush()

        result = gemini_helper.answer_question(georgian_question, relevant_laws)

        print(f"[DEBUG] Gemini result error={result.get('error')}", flush=True)
        sys.stdout.flush()

        # Step 4: Add to conversation history
        if 'conversation_history' not in session:
            session['conversation_history'] = []

        session['conversation_history'].append({
            'question': georgian_question,
            'answer': result['answer'],
            'sources': result['sources'],
            'timestamp': datetime.now().strftime('%H:%M')
        })
        session.modified = True

        # Prepare response with law details
        relevant_laws_data = [
            {
                'filename': law.filename,
                'law_name': law.law_name,
                'summary_en': law.summary_en
            }
            for law in relevant_laws
        ]

        return jsonify({
            'answer': result['answer'],
            'sources': result['sources'],
            'relevant_laws': relevant_laws_data,
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
        data = request.get_json() or {}
        num_questions = data.get('num_questions', 10)

        # Get random questions
        questions = quiz_db.get_random_questions(limit=num_questions)

        print(f"[DEBUG] Got {len(questions)} questions from database")
        if questions:
            print(f"[DEBUG] First question ID: {questions[0]['id']}, type: {type(questions[0]['id'])}")
            print(f"[DEBUG] Question IDs: {[q['id'] for q in questions]}")

        if not questions:
            return jsonify({
                'error': True,
                'message': 'კითხვები ჯერ არ არის გენერირებული. გაუშვით quiz_generator.py'
            }), 400

        # Store only question IDs in session (to keep session cookie small)
        session['current_quiz'] = {
            'question_ids': [q['id'] for q in questions],
            'current_index': 0,
            'start_time': datetime.now().isoformat()
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

        # Record answer
        quiz_db.record_answer(
            session['quiz_session_id'],
            question_id,
            user_answer,
            is_correct
        )

        # Move to next question
        quiz = session['current_quiz']
        quiz['current_index'] += 1
        session.modified = True

        # Check if quiz is complete
        total_questions = len(quiz['question_ids'])
        if quiz['current_index'] >= total_questions:
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

        return jsonify({
            'is_correct': is_correct,
            'correct_answer': correct_answer,
            'user_answer': user_answer,
            'explanation': explanation,
            'law_reference': law_reference,
            'next_question': next_question,
            'is_complete': is_complete,
            'current_index': quiz['current_index'],
            'total_questions': total_questions
        })

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
