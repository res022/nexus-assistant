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
                quality_score INTEGER DEFAULT 0,
                is_approved INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

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

        conn.commit()
        conn.close()
        print(f"[INFO] Database initialized at {self.db_path}")

    def add_question(self, question_data):
        """Add a new quiz question"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO quiz_questions
            (question_text, options, correct_answer, explanation, law_reference, category, difficulty, is_approved)
            VALUES (?, ?, ?, ?, ?, ?, ?, 1)
        ''', (
            question_data['question'],
            json.dumps(question_data['options']),
            question_data['correct_answer'],
            question_data['explanation'],
            question_data['law_reference'],
            question_data['category'],
            question_data['difficulty']
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

    def get_random_questions(self, limit=10):
        """Get random approved questions (mixed difficulty and topics)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, question_text, options, correct_answer, explanation, law_reference, category, difficulty
            FROM quiz_questions
            WHERE is_approved = 1
            ORDER BY RANDOM()
            LIMIT ?
        ''', (limit,))

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
