# -*- coding: utf-8 -*-
"""
User Manager - Handle user accounts, authentication, and profiles
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for


class UserManager:
    """Manage user accounts and authentication"""

    def __init__(self, db_path='quiz_data.db'):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        """Create users table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                display_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                total_quizzes INTEGER DEFAULT 0,
                total_correct INTEGER DEFAULT 0,
                total_questions INTEGER DEFAULT 0
            )
        ''')

        # User quiz sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_quiz_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                total_questions INTEGER DEFAULT 0,
                correct_answers INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')

        # User quiz answers table (detailed history)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_quiz_answers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id INTEGER,
                question_id INTEGER NOT NULL,
                user_answer TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (session_id) REFERENCES user_quiz_sessions (id),
                FOREIGN KEY (question_id) REFERENCES quiz_questions (id)
            )
        ''')

        conn.commit()
        conn.close()

    def hash_password(self, password):
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"

    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        try:
            salt, pwd_hash = password_hash.split('$')
            return pwd_hash == hashlib.sha256((password + salt).encode()).hexdigest()
        except:
            return False

    def create_user(self, username, email, password, display_name=None):
        """Create a new user account"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            password_hash = self.hash_password(password)
            display_name = display_name or username

            cursor.execute('''
                INSERT INTO users (username, email, password_hash, display_name)
                VALUES (?, ?, ?, ?)
            ''', (username, email, password_hash, display_name))

            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return {'success': True, 'user_id': user_id}

        except sqlite3.IntegrityError as e:
            conn.close()
            if 'username' in str(e):
                return {'success': False, 'error': 'Username already exists'}
            elif 'email' in str(e):
                return {'success': False, 'error': 'Email already exists'}
            else:
                return {'success': False, 'error': 'Registration failed'}

    def authenticate_user(self, username, password):
        """Authenticate user with username and password"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, username, email, password_hash, display_name, is_active
            FROM users
            WHERE username = ? OR email = ?
        ''', (username, username))

        user = cursor.fetchone()
        conn.close()

        if not user:
            return {'success': False, 'error': 'Invalid username or password'}

        user_id, username, email, password_hash, display_name, is_active = user

        if not is_active:
            return {'success': False, 'error': 'Account is disabled'}

        if not self.verify_password(password, password_hash):
            return {'success': False, 'error': 'Invalid username or password'}

        # Update last login
        self.update_last_login(user_id)

        return {
            'success': True,
            'user': {
                'id': user_id,
                'username': username,
                'email': email,
                'display_name': display_name
            }
        }

    def update_last_login(self, user_id):
        """Update user's last login timestamp"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (user_id,))

        conn.commit()
        conn.close()

    def get_user_by_id(self, user_id):
        """Get user information by ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, username, email, display_name, created_at, last_login,
                   total_quizzes, total_correct, total_questions
            FROM users
            WHERE id = ?
        ''', (user_id,))

        user = cursor.fetchone()
        conn.close()

        if not user:
            return None

        return {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'display_name': user[3],
            'created_at': user[4],
            'last_login': user[5],
            'total_quizzes': user[6],
            'total_correct': user[7],
            'total_questions': user[8],
            'accuracy': round((user[7] / user[8] * 100) if user[8] > 0 else 0, 1)
        }

    def get_user_stats(self, user_id):
        """Get detailed user statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Overall stats
        cursor.execute('''
            SELECT total_quizzes, total_correct, total_questions
            FROM users
            WHERE id = ?
        ''', (user_id,))
        overall = cursor.fetchone()

        # Category breakdown
        cursor.execute('''
            SELECT q.category,
                   COUNT(*) as total,
                   SUM(ua.is_correct) as correct
            FROM user_quiz_answers ua
            JOIN quiz_questions q ON ua.question_id = q.id
            WHERE ua.user_id = ?
            GROUP BY q.category
        ''', (user_id,))
        categories = cursor.fetchall()

        # Difficulty breakdown
        cursor.execute('''
            SELECT q.difficulty,
                   COUNT(*) as total,
                   SUM(ua.is_correct) as correct
            FROM user_quiz_answers ua
            JOIN quiz_questions q ON ua.question_id = q.id
            WHERE ua.user_id = ?
            GROUP BY q.difficulty
        ''', (user_id,))
        difficulties = cursor.fetchall()

        # Recent quiz sessions
        cursor.execute('''
            SELECT id, started_at, completed_at, total_questions, correct_answers
            FROM user_quiz_sessions
            WHERE user_id = ?
            ORDER BY started_at DESC
            LIMIT 10
        ''', (user_id,))
        recent_sessions = cursor.fetchall()

        conn.close()

        return {
            'total_quizzes': overall[0] if overall else 0,
            'total_correct': overall[1] if overall else 0,
            'total_questions': overall[2] if overall else 0,
            'accuracy': round((overall[1] / overall[2] * 100) if overall and overall[2] > 0 else 0, 1),
            'categories': [{'name': c[0], 'total': c[1], 'correct': c[2]} for c in categories],
            'difficulties': [{'name': d[0], 'total': d[1], 'correct': d[2]} for d in difficulties],
            'recent_sessions': [
                {
                    'id': s[0],
                    'started_at': s[1],
                    'completed_at': s[2],
                    'total': s[3],
                    'correct': s[4],
                    'accuracy': round((s[4] / s[3] * 100) if s[3] > 0 else 0, 1)
                }
                for s in recent_sessions
            ]
        }

    def record_quiz_answer(self, user_id, session_id, question_id, user_answer, is_correct):
        """Record a quiz answer for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO user_quiz_answers (user_id, session_id, question_id, user_answer, is_correct)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, session_id, question_id, user_answer, is_correct))

        # Update user totals
        cursor.execute('''
            UPDATE users
            SET total_questions = total_questions + 1,
                total_correct = total_correct + ?
            WHERE id = ?
        ''', (1 if is_correct else 0, user_id))

        conn.commit()
        conn.close()

    def start_quiz_session(self, user_id):
        """Start a new quiz session for a user"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO user_quiz_sessions (user_id)
            VALUES (?)
        ''', (user_id,))

        session_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return session_id

    def complete_quiz_session(self, session_id, total_questions, correct_answers):
        """Complete a quiz session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            UPDATE user_quiz_sessions
            SET completed_at = CURRENT_TIMESTAMP,
                total_questions = ?,
                correct_answers = ?
            WHERE id = ?
        ''', (total_questions, correct_answers, session_id))

        # Update user's total quiz count
        cursor.execute('''
            UPDATE users
            SET total_quizzes = total_quizzes + 1
            WHERE id = (SELECT user_id FROM user_quiz_sessions WHERE id = ?)
        ''', (session_id,))

        conn.commit()
        conn.close()

    def get_leaderboard(self, limit=10):
        """Get top users by accuracy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT username, display_name, total_quizzes, total_correct, total_questions,
                   ROUND(CAST(total_correct AS FLOAT) / total_questions * 100, 1) as accuracy
            FROM users
            WHERE total_questions >= 10
            ORDER BY accuracy DESC, total_questions DESC
            LIMIT ?
        ''', (limit,))

        leaderboard = cursor.fetchall()
        conn.close()

        return [
            {
                'username': row[0],
                'display_name': row[1],
                'total_quizzes': row[2],
                'total_correct': row[3],
                'total_questions': row[4],
                'accuracy': row[5]
            }
            for row in leaderboard
        ]


def user_login_required(f):
    """Decorator to require user login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('user_login'))
        return f(*args, **kwargs)
    return decorated_function
