# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('quiz_data.db')
cursor = conn.cursor()

# Get 10 random rules questions and show their details
print("\n=== TESTING: Get 10 random RULES questions ===")
cursor.execute('''
    SELECT id, source_type, category, law_reference
    FROM quiz_questions
    WHERE source_type = "rules"
    ORDER BY RANDOM()
    LIMIT 10
''')

rules_questions = cursor.fetchall()
print(f"Retrieved {len(rules_questions)} rules questions:")
for q in rules_questions:
    print(f"  ID: {q[0]}, Source: {q[1]}, Category: {q[2]}")

# Check if any questions have wrong source_type
print("\n=== Checking for data corruption ===")
cursor.execute('''
    SELECT COUNT(*)
    FROM quiz_questions
    WHERE source_type = "rules"
    AND (law_reference LIKE "%კანონი%" OR law_reference LIKE "%პროკურატურის%")
''')
wrong_refs = cursor.fetchone()[0]
print(f"Rules questions with law references (corruption): {wrong_refs}")

# Check the specific question about police officer
print("\n=== Looking for police officer question ===")
cursor.execute('''
    SELECT id, source_type, category, law_reference
    FROM quiz_questions
    WHERE question_text LIKE "%პოლიცი%"
    LIMIT 5
''')
police_q = cursor.fetchall()
for q in police_q:
    print(f"  ID: {q[0]}, Source: {q[1]}, Cat: {q[2]}, Ref: {q[3][:50]}")

conn.close()
