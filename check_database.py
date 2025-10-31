# -*- coding: utf-8 -*-
"""
Quick database diagnostic script
"""

import sqlite3
import json

db_path = 'quiz_data.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("="*60)
print("   Database Diagnostic Report")
print("="*60)

# Total questions
cursor.execute('SELECT COUNT(*) FROM quiz_questions')
total = cursor.fetchone()[0]
print(f"\n[TOTAL] Questions in database: {total}")

# Approved questions
cursor.execute('SELECT COUNT(*) FROM quiz_questions WHERE is_approved = 1')
approved = cursor.fetchone()[0]
print(f"[APPROVED] Approved questions: {approved}")

# Sample question IDs
cursor.execute('SELECT id, is_approved FROM quiz_questions LIMIT 10')
samples = cursor.fetchall()

print(f"\n[SAMPLES] Sample question IDs:")
for row in samples:
    status = "APPROVED" if row[1] == 1 else "NOT APPROVED"
    print(f"  ID {row[0]}: {status}")

# Questions by category
cursor.execute('SELECT COUNT(DISTINCT category) FROM quiz_questions WHERE is_approved = 1')
category_count = cursor.fetchone()[0]
print(f"\n[CATEGORIES] Total categories: {category_count}")

# Questions by difficulty
cursor.execute('SELECT difficulty, COUNT(*) FROM quiz_questions WHERE is_approved = 1 GROUP BY difficulty')
difficulties = cursor.fetchall()
print(f"\n[DIFFICULTY] Questions by difficulty:")
for diff, count in difficulties:
    print(f"  {diff}: {count} questions")

conn.close()

print("\n" + "="*60)
