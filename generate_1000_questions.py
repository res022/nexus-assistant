# -*- coding: utf-8 -*-
"""
Generate 1000 quiz questions in TWO PASSES for reliability
Pass 1: 13 questions per law = ~494 questions
Pass 2: 13 more questions per law = ~494 questions
Total: ~988 questions
"""

from quiz_generator import QuizGenerator

print("="*60)
print("   Generating 1000 Quiz Questions (2 Passes)")
print("="*60)

generator = QuizGenerator()

print("\n[INFO] Using 2-pass approach for maximum reliability")
print("[INFO] Pass 1: 13 questions per law = ~494 questions")
print("[INFO] Pass 2: 13 questions per law = ~494 questions")
print("[INFO] Total expected: ~988 questions")
print("[INFO] This will take approximately 15-20 minutes...\n")

# PASS 1: First 13 questions
print("="*60)
print("   PASS 1: Generating first 13 questions per law")
print("="*60)
total_pass1 = generator.generate_all_questions(questions_per_law=13)

print("\n[PASS 1 COMPLETE] Generated " + str(total_pass1) + " questions")
print("[INFO] Starting Pass 2 in 5 seconds...\n")

import time
time.sleep(5)

# PASS 2: Another 13 questions
print("="*60)
print("   PASS 2: Generating 13 more questions per law")
print("="*60)
total_pass2 = generator.generate_all_questions(questions_per_law=13)

print("\n[PASS 2 COMPLETE] Generated " + str(total_pass2) + " questions")

# Final summary
total = total_pass1 + total_pass2
print("\n" + "="*60)
print(f"   PASSES COMPLETE! Generated {total} questions")
print(f"   Pass 1: {total_pass1} questions")
print(f"   Pass 2: {total_pass2} questions")
print("="*60)

# Check if we got questions from all 38 laws
from database import QuizDatabase
db = QuizDatabase()
import sqlite3
conn = sqlite3.connect(db.db_path)
cursor = conn.cursor()

# Get distinct law references
cursor.execute('''
    SELECT DISTINCT law_reference FROM quiz_questions
''')
distinct_laws = cursor.fetchall()
conn.close()

print(f"\n[INFO] Questions generated from {len(distinct_laws)} different laws")
print(f"[INFO] Target was 38 laws")

if len(distinct_laws) < 38:
    print(f"\n[WARNING] Some laws may have failed. This is expected with API limits.")
    print(f"[INFO] You have {total} questions total - more than enough for a great quiz!")

print("\n" + "="*60)
print(f"   FINAL: {total} questions ready to use!")
print("="*60)
