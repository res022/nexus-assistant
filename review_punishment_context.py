# -*- coding: utf-8 -*-
"""
Review punishment translation fixes to ensure they're contextually correct
"""

import sqlite3
import json

def review_fixes():
    """Review all questions that were fixed to check context"""
    conn = sqlite3.connect('quiz_data.db')
    cursor = conn.cursor()

    # Get all questions with "სპეც ციხე"
    cursor.execute("""
        SELECT id, question_text, options, correct_answer, explanation, source_type, law_reference
        FROM quiz_questions
        WHERE (question_text LIKE '%სპეც ციხე%'
           OR options LIKE '%სპეც ციხე%'
           OR correct_answer LIKE '%სპეც ციხე%'
           OR explanation LIKE '%სპეც ციხე%')
    """)

    results = cursor.fetchall()

    print(f"Total questions with 'spec jail' translation: {len(results)}")
    print("="*80)

    # Keywords that indicate OOC/server rules punishment context
    ooc_keywords = [
        'ადმინისტრაცია', 'ადმინი', 'მოდერატორი', 'წესების დარღვევა',
        'სერვერის წესი', 'OOC', 'სანქცია', 'გაფრთხილება', 'BAN', 'MUTE',
        'spec jail', 'სპეც ციხე'
    ]

    # Keywords that indicate IC/roleplay context
    ic_keywords = [
        'დაპატიმრება', 'პატიმარი', 'ციხის მცველი', 'სასამართლო',
        'მსაჯული', 'გამოძიება', 'დაკითხვა', 'ორდერი', 'IC', 'roleplay',
        'პროკურორი', 'პოლიცია', 'ფრაქცია'
    ]

    ooc_count = 0
    ic_count = 0
    unclear_count = 0

    for row in results:
        qid, question, options_json, correct, explanation, source, law_ref = row

        # Combine all text for context analysis
        all_text = f"{question} {options_json} {correct} {explanation} {law_ref}"

        # Check context
        has_ooc = any(keyword in all_text for keyword in ooc_keywords)
        has_ic = any(keyword in all_text for keyword in ic_keywords)

        if has_ooc and not has_ic:
            ooc_count += 1
            context = "OOC (server punishment) - CORRECT"
        elif has_ic and not has_ooc:
            ic_count += 1
            context = "IC (roleplay) - MAY BE INCORRECT"
            print(f"\nQuestion ID {qid}: {context}")
            print(f"Law Reference: {law_ref}")
            print(f"Question: {question[:150]}...")
            print("-"*80)
        else:
            unclear_count += 1
            context = "UNCLEAR CONTEXT"

    print("\n" + "="*80)
    print("SUMMARY:")
    print(f"  OOC/Server Rules Context (correct): {ooc_count}")
    print(f"  IC/Roleplay Context (may need revert): {ic_count}")
    print(f"  Unclear Context: {unclear_count}")
    print("="*80)

    conn.close()

if __name__ == '__main__':
    review_fixes()
