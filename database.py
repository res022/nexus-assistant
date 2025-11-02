# -*- coding: utf-8 -*-
"""
Database handler for quiz system
"""

import sqlite3
import json
from datetime import datetime
import os

class QuizDatabase:
    """Handles quiz questions and user progress storage"""

    def __init__(self, db_path='quiz_data.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Quiz questions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                explanation TEXT NOT NULL,
                law_reference TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                source_type TEXT DEFAULT 'laws',
                quality_score INTEGER DEFAULT 0,
                is_approved INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Add source_type column to existing table if it doesn't exist
        try:
            cursor.execute('ALTER TABLE quiz_questions ADD COLUMN source_type TEXT DEFAULT "laws"')
        except sqlite3.OperationalError:
            pass  # Column already exists

        # User progress table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty_level INTEGER DEFAULT 1,
                questions_answered INTEGER DEFAULT 0,
                questions_correct INTEGER DEFAULT 0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Quiz history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quiz_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question_id INTEGER NOT NULL,
                user_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                time_taken INTEGER,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (question_id) REFERENCES quiz_questions(id)
            )
        ''')

        # Shared quizzes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_quizzes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                question_ids TEXT NOT NULL,
                created_by_admin TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')

        # Shared quiz attempts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS shared_quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                quiz_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                answers_json TEXT NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                can_retake INTEGER DEFAULT 0,
                FOREIGN KEY (quiz_id) REFERENCES shared_quizzes(quiz_id),
                UNIQUE(quiz_id, user_id)
            )
        ''')

        # Multiplayer matches table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS multiplayer_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT UNIQUE NOT NULL,
                creator_id INTEGER NOT NULL,
                opponent_id INTEGER,
                question_ids TEXT NOT NULL,
                num_questions INTEGER NOT NULL,
                difficulty TEXT,
                source_type TEXT DEFAULT 'laws',
                status TEXT DEFAULT 'waiting',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                started_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')

        # Multiplayer match results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS multiplayer_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                match_id TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                answers_json TEXT NOT NULL,
                times_json TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_time INTEGER NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (match_id) REFERENCES multiplayer_matches(match_id)
            )
        ''')

        conn.commit()
        conn.close()
        print(f"[INFO] Database initialized at {self.db_path}")

    def add_question(self, question_data):
        """Add a new quiz question"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO quiz_questions
            (question_text, options, correct_answer, explanation, law_reference, category, difficulty, source_type, is_approved)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 1)
        ''', (
            question_data['question'],
            json.dumps(question_data['options']),
            question_data['correct_answer'],
            question_data['explanation'],
            question_data['law_reference'],
            question_data['category'],
            question_data['difficulty'],
            question_data.get('source_type', 'laws')
        ))

        conn.commit()
        question_id = cursor.lastrowid
        conn.close()
        return question_id

    def get_questions_by_category_difficulty(self, category, difficulty, limit=10):
        """Get approved questions by category and difficulty"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, question_text, options, correct_answer, explanation, law_reference, category, difficulty
            FROM quiz_questions
            WHERE category = ? AND difficulty = ? AND is_approved = 1
            ORDER BY RANDOM()
            LIMIT ?
        ''', (category, difficulty, limit))

        results = cursor.fetchall()
        conn.close()

        questions = []
        for row in results:
            questions.append({
                'id': row[0],
                'question': row[1],
                'options': json.loads(row[2]),
                'correct_answer': row[3],
                'explanation': row[4],
                'law_reference': row[5],
                'category': row[6],
                'difficulty': row[7]
            })

        return questions

    def get_random_questions(self, limit=10, source_type='laws', difficulty=None):
        """Get random approved questions (mixed difficulty and topics)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Build query with optional difficulty filter
        if difficulty:
            cursor.execute('''
                SELECT id, question_text, options, correct_answer, explanation, law_reference, category, difficulty, source_type
                FROM quiz_questions
                WHERE is_approved = 1 AND source_type = ? AND difficulty = ?
                ORDER BY RANDOM()
                LIMIT ?
            ''', (source_type, difficulty, limit))
        else:
            cursor.execute('''
                SELECT id, question_text, options, correct_answer, explanation, law_reference, category, difficulty, source_type
                FROM quiz_questions
                WHERE is_approved = 1 AND source_type = ?
                ORDER BY RANDOM()
                LIMIT ?
            ''', (source_type, limit))

        results = cursor.fetchall()
        conn.close()

        questions = []
        for row in results:
            questions.append({
                'id': row[0],
                'question': row[1],
                'options': json.loads(row[2]),
                'correct_answer': row[3],
                'explanation': row[4],
                'law_reference': row[5],
                'category': row[6],
                'difficulty': row[7],
                'source_type': row[8]
            })

        return questions

    def record_answer(self, session_id, question_id, user_answer, is_correct, time_taken=None):
        """Record user's answer to a question"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO quiz_history (session_id, question_id, user_answer, is_correct, time_taken)
            VALUES (?, ?, ?, ?, ?)
        ''', (session_id, question_id, user_answer, 1 if is_correct else 0, time_taken))

        conn.commit()
        conn.close()

    def get_user_stats(self, session_id):
        """Get user's quiz statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Overall stats
        cursor.execute('''
            SELECT
                COUNT(*) as total,
                SUM(is_correct) as correct
            FROM quiz_history
            WHERE session_id = ?
        ''', (session_id,))

        overall = cursor.fetchone()

        # Stats by category
        cursor.execute('''
            SELECT
                q.category,
                COUNT(*) as total,
                SUM(h.is_correct) as correct
            FROM quiz_history h
            JOIN quiz_questions q ON h.question_id = q.id
            WHERE h.session_id = ?
            GROUP BY q.category
        ''', (session_id,))

        by_category = cursor.fetchall()
        conn.close()

        stats = {
            'total_answered': overall[0] if overall else 0,
            'total_correct': overall[1] if overall else 0,
            'accuracy': (overall[1] / overall[0] * 100) if overall and overall[0] > 0 else 0,
            'by_category': {}
        }

        for row in by_category:
            stats['by_category'][row[0]] = {
                'total': row[1],
                'correct': row[2],
                'accuracy': (row[2] / row[1] * 100) if row[1] > 0 else 0
            }

        return stats

    def get_question_count(self):
        """Get total number of approved questions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM quiz_questions WHERE is_approved = 1')
        count = cursor.fetchone()[0]

        conn.close()
        return count

    # ============================================================================
    # SHARED QUIZ METHODS
    # ============================================================================

    def create_shared_quiz(self, quiz_id, title, description, question_ids, admin_username):
        """Create a new shared quiz"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO shared_quizzes (quiz_id, title, description, question_ids, created_by_admin)
            VALUES (?, ?, ?, ?, ?)
        ''', (quiz_id, title, description, json.dumps(question_ids), admin_username))

        conn.commit()
        conn.close()
        return quiz_id

    def get_shared_quiz(self, quiz_id):
        """Get shared quiz details"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM shared_quizzes WHERE quiz_id = ? AND is_active = 1
        ''', (quiz_id,))

        quiz = cursor.fetchone()
        conn.close()

        if quiz:
            quiz_dict = dict(quiz)
            quiz_dict['question_ids'] = json.loads(quiz_dict['question_ids'])
            return quiz_dict
        return None

    def get_shared_quiz_questions(self, quiz_id):
        """Get all questions for a shared quiz"""
        quiz = self.get_shared_quiz(quiz_id)
        if not quiz:
            return None

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        placeholders = ','.join('?' * len(quiz['question_ids']))
        cursor.execute(f'''
            SELECT id, question_text, options, correct_answer, explanation, law_reference, category, difficulty
            FROM quiz_questions
            WHERE id IN ({placeholders}) AND is_approved = 1
        ''', quiz['question_ids'])

        questions = []
        for row in cursor.fetchall():
            q = dict(row)
            q['options'] = json.loads(q['options'])
            questions.append(q)

        conn.close()
        return questions

    def check_user_attempt(self, quiz_id, user_id):
        """Check if user has attempted this quiz"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, score, total_questions, can_retake, completed_at
            FROM shared_quiz_attempts
            WHERE quiz_id = ? AND user_id = ?
        ''', (quiz_id, user_id))

        attempt = cursor.fetchone()
        conn.close()

        if attempt:
            return {
                'has_attempted': True,
                'score': attempt[1],
                'total_questions': attempt[2],
                'can_retake': bool(attempt[3]),
                'completed_at': attempt[4]
            }
        return {'has_attempted': False}

    def record_shared_quiz_attempt(self, quiz_id, user_id, score, total_questions, answers):
        """Record a shared quiz attempt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if attempt already exists and get can_retake status
        cursor.execute('SELECT id, can_retake FROM shared_quiz_attempts WHERE quiz_id = ? AND user_id = ?',
                      (quiz_id, user_id))
        existing = cursor.fetchone()

        if existing:
            # Update existing attempt (only if can_retake is true)
            # Reset can_retake to 0 after the retake is used
            if existing[1] == 1:  # can_retake is True
                cursor.execute('''
                    UPDATE shared_quiz_attempts
                    SET score = ?, total_questions = ?, answers_json = ?, completed_at = CURRENT_TIMESTAMP, can_retake = 0
                    WHERE id = ?
                ''', (score, total_questions, json.dumps(answers), existing[0]))
                conn.commit()
                conn.close()
                return True
            else:
                # User tried to submit without retake permission
                conn.close()
                return False
        else:
            # Insert new attempt
            cursor.execute('''
                INSERT INTO shared_quiz_attempts (quiz_id, user_id, score, total_questions, answers_json)
                VALUES (?, ?, ?, ?, ?)
            ''', (quiz_id, user_id, score, total_questions, json.dumps(answers)))
            conn.commit()
            conn.close()
            return True

    def allow_retake(self, quiz_id, user_id):
        """Allow a user to retake a shared quiz"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE shared_quiz_attempts
            SET can_retake = 1
            WHERE quiz_id = ? AND user_id = ?
        ''', (quiz_id, user_id))

        conn.commit()
        affected = cursor.rowcount
        conn.close()
        return affected > 0

    def get_quiz_attempts(self, quiz_id):
        """Get all attempts for a quiz (for admin view)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT a.*, u.username, u.display_name
            FROM shared_quiz_attempts a
            JOIN users u ON a.user_id = u.id
            WHERE a.quiz_id = ?
            ORDER BY a.completed_at DESC
        ''', (quiz_id,))

        attempts = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return attempts

    def get_all_shared_quizzes(self):
        """Get all shared quizzes (for admin)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, quiz_id, title, description, question_ids, created_by_admin, created_at, is_active,
                   (SELECT COUNT(*) FROM shared_quiz_attempts WHERE quiz_id = shared_quizzes.quiz_id) as attempt_count
            FROM shared_quizzes
            ORDER BY created_at DESC
        ''')

        quizzes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return quizzes

    def toggle_quiz_active(self, quiz_id):
        """Toggle quiz active status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('UPDATE shared_quizzes SET is_active = NOT is_active WHERE quiz_id = ?', (quiz_id,))

        conn.commit()
        conn.close()

    # =========================================================================
    # MULTIPLAYER MATCH METHODS
    # =========================================================================

    def create_multiplayer_match(self, creator_id, num_questions=10, difficulty=None, source_type='laws'):
        """Create a new multiplayer match"""
        import uuid

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Generate unique match ID
        match_id = str(uuid.uuid4())[:8]

        # Get random questions
        questions = self.get_random_questions(limit=num_questions, source_type=source_type, difficulty=difficulty)
        question_ids = [q['id'] for q in questions]

        cursor.execute('''
            INSERT INTO multiplayer_matches
            (match_id, creator_id, question_ids, num_questions, difficulty, source_type, status)
            VALUES (?, ?, ?, ?, ?, ?, 'waiting')
        ''', (match_id, creator_id, json.dumps(question_ids), num_questions, difficulty or 'mixed', source_type))

        conn.commit()
        conn.close()

        return match_id

    def join_multiplayer_match(self, match_id, user_id):
        """Join an existing multiplayer match"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Check if match exists and is waiting
        cursor.execute('SELECT status, creator_id FROM multiplayer_matches WHERE match_id = ?', (match_id,))
        result = cursor.fetchone()

        if not result:
            conn.close()
            return {'success': False, 'message': 'Match not found'}

        status, creator_id = result

        if status != 'waiting':
            conn.close()
            return {'success': False, 'message': 'Match already started or finished'}

        if creator_id == user_id:
            conn.close()
            return {'success': False, 'message': 'Cannot join your own match'}

        # Update match with opponent and start it
        cursor.execute('''
            UPDATE multiplayer_matches
            SET opponent_id = ?, status = 'in_progress', started_at = CURRENT_TIMESTAMP
            WHERE match_id = ?
        ''', (user_id, match_id))

        conn.commit()
        conn.close()

        return {'success': True}

    def get_multiplayer_match(self, match_id):
        """Get match details"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM multiplayer_matches WHERE match_id = ?', (match_id,))
        match = cursor.fetchone()

        if not match:
            conn.close()
            return None

        match_dict = dict(match)
        match_dict['question_ids'] = json.loads(match_dict['question_ids'])

        conn.close()
        return match_dict

    def get_match_questions(self, match_id):
        """Get all questions for a match"""
        match = self.get_multiplayer_match(match_id)

        if not match:
            return []

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        question_ids = match['question_ids']
        placeholders = ','.join('?' * len(question_ids))

        cursor.execute(f'''
            SELECT id, question_text, options, correct_answer, explanation, law_reference, difficulty
            FROM quiz_questions
            WHERE id IN ({placeholders})
        ''', question_ids)

        results = cursor.fetchall()
        conn.close()

        # Preserve order
        questions_dict = {}
        for row in results:
            questions_dict[row[0]] = {
                'id': row[0],
                'question': row[1],
                'options': json.loads(row[2]),
                'correct_answer': row[3],
                'explanation': row[4],
                'law_reference': row[5],
                'difficulty': row[6]
            }

        # Return in order
        return [questions_dict[qid] for qid in question_ids if qid in questions_dict]

    def submit_multiplayer_result(self, match_id, user_id, answers, times, score):
        """Submit multiplayer match results"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        total_time = sum(times)

        cursor.execute('''
            INSERT INTO multiplayer_results (match_id, user_id, answers_json, times_json, score, total_time)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (match_id, user_id, json.dumps(answers), json.dumps(times), score, total_time))

        # Check if both players finished
        cursor.execute('SELECT COUNT(*) FROM multiplayer_results WHERE match_id = ?', (match_id,))
        count = cursor.fetchone()[0]

        if count >= 2:
            # Both finished, mark match as completed
            cursor.execute('''
                UPDATE multiplayer_matches
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE match_id = ?
            ''', (match_id,))

        conn.commit()
        conn.close()

    def get_multiplayer_results(self, match_id):
        """Get results for both players"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT mr.*, u.display_name, u.username
            FROM multiplayer_results mr
            LEFT JOIN users u ON mr.user_id = u.id
            WHERE mr.match_id = ?
            ORDER BY mr.score DESC, mr.total_time ASC
        ''', (match_id,))

        results = cursor.fetchall()
        conn.close()

        return [dict(row) for row in results]

    def get_waiting_matches(self, limit=10):
        """Get list of matches waiting for opponents"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT m.*, u.display_name as creator_name
            FROM multiplayer_matches m
            LEFT JOIN users u ON m.creator_id = u.id
            WHERE m.status = 'waiting'
            ORDER BY m.created_at DESC
            LIMIT ?
        ''', (limit,))

        matches = cursor.fetchall()
        conn.close()

        return [dict(row) for row in matches]

    def get_user_matches(self, user_id, limit=10):
        """Get user's recent matches"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute('''
            SELECT m.*,
                   u1.display_name as creator_name,
                   u2.display_name as opponent_name
            FROM multiplayer_matches m
            LEFT JOIN users u1 ON m.creator_id = u1.id
            LEFT JOIN users u2 ON m.opponent_id = u2.id
            WHERE m.creator_id = ? OR m.opponent_id = ?
            ORDER BY m.created_at DESC
            LIMIT ?
        ''', (user_id, user_id, limit))

        matches = cursor.fetchall()
        conn.close()

        return [dict(row) for row in matches]
