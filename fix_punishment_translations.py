# -*- coding: utf-8 -*-
"""
Fix incorrect Georgian punishment translations in quiz database
"""

import sqlite3
import json

# Translation mapping: incorrect -> correct
PUNISHMENT_TRANSLATIONS = {
    'დააპატიმრო': 'სპეც ციხეში ჩასმა',
    'დააპატიმრეთ': 'სპეც ციხეში ჩასმა',
    'პატიმრობა': 'სპეც ციხე',
    'დაპატიმრება': 'სპეც ციხეში ჩასმა',
    'ციხეში ჩასმა': 'სპეც ციხეში ჩასმა',
    'ციხე': 'სპეც ციხე',
    'Demorgan': 'სპეც ციხე',
    'DeMorgan': 'სპეც ციხე',
    'demorgan': 'სპეც ციხე',
}

def fix_translations():
    """Find and fix incorrect punishment translations"""
    conn = sqlite3.connect('quiz_data.db')
    cursor = conn.cursor()

    # Get all questions
    cursor.execute("SELECT id, question_text, options, correct_answer, explanation FROM quiz_questions")
    all_questions = cursor.fetchall()

    fixed_count = 0

    for question in all_questions:
        qid, question_text, options_json, correct_answer, explanation = question

        # Parse options
        try:
            options = json.loads(options_json)
        except:
            print(f"[WARN] Could not parse options for question {qid}")
            continue

        # Check if any field needs fixing
        needs_update = False

        # Fix question text
        new_question_text = question_text
        for old, new in PUNISHMENT_TRANSLATIONS.items():
            if old in new_question_text:
                new_question_text = new_question_text.replace(old, new)
                needs_update = True
                print(f"[FIX] Question {qid}: punishment term updated in question text")

        # Fix options
        new_options = []
        for opt in options:
            new_opt = opt
            for old, new in PUNISHMENT_TRANSLATIONS.items():
                if old in new_opt:
                    new_opt = new_opt.replace(old, new)
                    needs_update = True
                    print(f"[FIX] Question {qid}: punishment term updated in option")
            new_options.append(new_opt)

        # Fix correct answer
        new_correct_answer = correct_answer
        for old, new in PUNISHMENT_TRANSLATIONS.items():
            if old in new_correct_answer:
                new_correct_answer = new_correct_answer.replace(old, new)
                needs_update = True
                print(f"[FIX] Question {qid}: punishment term updated in correct answer")

        # Fix explanation
        new_explanation = explanation
        for old, new in PUNISHMENT_TRANSLATIONS.items():
            if old in new_explanation:
                new_explanation = new_explanation.replace(old, new)
                needs_update = True
                print(f"[FIX] Question {qid}: punishment term updated in explanation")

        # Update database if needed
        if needs_update:
            cursor.execute('''
                UPDATE quiz_questions
                SET question_text = ?,
                    options = ?,
                    correct_answer = ?,
                    explanation = ?
                WHERE id = ?
            ''', (new_question_text, json.dumps(new_options, ensure_ascii=False),
                  new_correct_answer, new_explanation, qid))
            fixed_count += 1

    conn.commit()
    conn.close()

    print(f"\n{'='*80}")
    print(f"[DONE] Fixed {fixed_count} questions with incorrect translations")
    print(f"{'='*80}")

if __name__ == '__main__':
    print("Starting punishment translation fixes...")
    print("="*80)
    fix_translations()
