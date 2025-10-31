# -*- coding: utf-8 -*-
"""
Admin Helper - Authentication and Admin Operations
"""

from functools import wraps
from flask import session, redirect, url_for, flash
from config import Config
import hashlib


def check_admin_auth(username, password):
    """Check if admin credentials are correct"""
    return (username == Config.ADMIN_USERNAME and
            password == Config.ADMIN_PASSWORD)


def login_required(f):
    """Decorator to require admin login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function


def get_admin_stats(law_parser, quiz_db):
    """Get statistics for admin dashboard"""
    stats = {
        'total_laws': len(law_parser.laws),
        'total_questions': quiz_db.get_question_count(),
        'laws_with_metadata': sum(1 for law in law_parser.laws if law.summary_en),
        'recent_activity': []
    }

    # Get category breakdown
    import sqlite3
    conn = sqlite3.connect(quiz_db.db_path)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT category, COUNT(*) as count
        FROM quiz_questions
        WHERE is_approved = 1
        GROUP BY category
        ORDER BY count DESC
    ''')
    stats['questions_by_category'] = dict(cursor.fetchall())

    cursor.execute('''
        SELECT difficulty, COUNT(*) as count
        FROM quiz_questions
        WHERE is_approved = 1
        GROUP BY difficulty
    ''')
    stats['questions_by_difficulty'] = dict(cursor.fetchall())

    conn.close()

    return stats
