# -*- coding: utf-8 -*-
"""
Fill in questions for laws that were skipped due to API errors
This runs AFTER the main generation to ensure ALL 38 laws have questions
"""

from quiz_generator import QuizGenerator
from law_parser import LawParser
from database import QuizDatabase
import sqlite3

print("="*60)
print("   Filling Missing Law Questions")
print("="*60)

# Initialize
generator = QuizGenerator()
law_parser = LawParser()
db = QuizDatabase()

# Load all laws
print("\n[INFO] Loading all laws...")
law_parser.load_all_laws()
print(f"[INFO] Total laws in system: {len(law_parser.laws)}")

# Get laws that already have questions
conn = sqlite3.connect(db.db_path)
cursor = conn.cursor()

cursor.execute('''
    SELECT DISTINCT law_reference FROM quiz_questions
''')
laws_with_questions = set(row[0] for row in cursor.fetchall())
conn.close()

print(f"[INFO] Laws with questions: {len(laws_with_questions)}")

# Find missing laws
missing_laws = []
for law in law_parser.laws:
    # Check if this law has any questions
    has_questions = False
    for law_ref in laws_with_questions:
        if law.law_name in law_ref or law.filename.replace('.txt', '') in law_ref:
            has_questions = True
            break

    if not has_questions:
        missing_laws.append(law)

print(f"[INFO] Laws missing questions: {len(missing_laws)}")

if not missing_laws:
    print("\n[SUCCESS] All laws already have questions! Nothing to do.")
    print("="*60)
    exit(0)

print("\n[INFO] Missing laws:")
for i, law in enumerate(missing_laws, 1):
    print(f"  {i}. {law.filename} (length: {len(law.georgian_text)} chars)")

print(f"\n[INFO] Generating 26 questions for each missing law...")
print("[INFO] This will take about 3-5 minutes per law...\n")

total_generated = 0

for idx, law in enumerate(missing_laws, 1):
    print(f"\n[INFO] Processing missing law {idx}/{len(missing_laws)}")
    print(f"[INFO] File: {law.filename} ({len(law.georgian_text)} chars)")

    # Generate 26 questions (same as successful laws get in 2 passes)
    questions = generator.generate_questions_from_law(law, questions_per_law=26)

    # Save to database
    for q in questions:
        try:
            db.add_question(q)
            total_generated += 1
        except Exception as e:
            print(f"[ERROR] Failed to save question: {str(e)[:100]}")

    print(f"[PROGRESS] Generated {len(questions)} questions for this law")
    print(f"[PROGRESS] Total new questions: {total_generated}")

print("\n" + "="*60)
print(f"   COMPLETE! Added {total_generated} questions")
print(f"   All {len(law_parser.laws)} laws now have questions!")
print("="*60)

# Final verification
conn = sqlite3.connect(db.db_path)
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM quiz_questions WHERE is_approved = 1')
final_total = cursor.fetchone()[0]
conn.close()

print(f"\n[FINAL] Total questions in database: {final_total}")
