# -*- coding: utf-8 -*-
"""
Context-Aware Georgian Punishment Translation Fixer v2
Only replaces terms when they refer to OOC/server punishments
"""

import sqlite3
import json
import re

def is_ooc_punishment_context(text):
    """
    Check if the text is about OOC server punishments vs IC roleplay
    Returns True if OOC context, False if IC context
    """
    text_lower = text.lower()

    # Strong OOC indicators
    ooc_indicators = [
        'სერვერის წესი', 'წესების დარღვევა', 'ადმინისტრაცია',
        'მოდერატორი', 'spec jail', 'demorgan', 'ooc',
        'server rule', 'გაფრთხილება', 'ban', 'mute',
        'სანქცია', 'ადმინი მიმართავს', 'ადმინისთვის'
    ]

    # Strong IC/Roleplay indicators
    ic_indicators = [
        'დაკითხვა', 'ორდერი', 'სასამართლო', 'მსაჯული',
        'პროკურატურა', 'პოლიცია', 'გამოძიება', 'რეიდი',
        'ფრაქცია', 'ლიდერი', 'პატიმარი', 'ციხის მცველი',
        'roleplay', 'fear rp', '/me', '/do', 'ic მიზეზი'
    ]

    has_ooc = any(ind in text_lower for ind in ooc_indicators)
    has_ic = any(ind in text_lower for ind in ic_indicators)

    # If has OOC indicators and no IC indicators, it's OOC
    if has_ooc and not has_ic:
        return True

    # If has IC indicators, it's IC
    if has_ic:
        return False

    # Default: if source_type is 'rules', assume OOC
    return None  # Unclear

def smart_replace(text, old_term, new_term, context_text):
    """
    Replace old_term with new_term only if context suggests OOC punishment
    """
    if old_term not in text:
        return text, False

    is_ooc = is_ooc_punishment_context(context_text)

    if is_ooc or is_ooc is None:  # Replace if OOC or unclear (assuming rules context)
        return text.replace(old_term, new_term), True
    else:  # Don't replace if IC context
        return text, False

def revert_and_fix_smart():
    """
    Revert all previous fixes, then reapply smartly based on context
    """
    conn = sqlite3.connect('quiz_data.db')
    cursor = conn.cursor()

    print("STEP 1: Reverting all previous translations...")
    print("="*80)

    # Reverse mapping to revert
    REVERT_MAP = {
        'სპეც ციხეში ჩასმა': 'დააპატიმრო',
        'სპეც ციხე': 'პატიმრობა',
    }

    # Get all questions with current translations
    cursor.execute("SELECT id, question_text, options, correct_answer, explanation, source_type, law_reference FROM quiz_questions")
    all_questions = cursor.fetchall()

    reverted_count = 0

    for question in all_questions:
        qid, question_text, options_json, correct_answer, explanation, source_type, law_ref = question

        try:
            options = json.loads(options_json)
        except:
            continue

        needs_update = False
        new_question = question_text
        new_options = options[:]
        new_correct = correct_answer
        new_explanation = explanation

        # Revert translations
        for new_term, old_term in REVERT_MAP.items():
            if new_term in question_text:
                new_question = new_question.replace(new_term, old_term)
                needs_update = True

            if new_term in correct_answer:
                new_correct = new_correct.replace(new_term, old_term)
                needs_update = True

            if new_term in explanation:
                new_explanation = new_explanation.replace(new_term, old_term)
                needs_update = True

            for i, opt in enumerate(new_options):
                if new_term in opt:
                    new_options[i] = opt.replace(new_term, old_term)
                    needs_update = True

        if needs_update:
            cursor.execute('''
                UPDATE quiz_questions
                SET question_text = ?, options = ?, correct_answer = ?, explanation = ?
                WHERE id = ?
            ''', (new_question, json.dumps(new_options, ensure_ascii=False), new_correct, new_explanation, qid))
            reverted_count += 1

    conn.commit()
    print(f"Reverted {reverted_count} questions to original terms")

    print("\nSTEP 2: Applying smart context-aware translations...")
    print("="*80)

    # Now apply smart translations
    SMART_TRANSLATIONS = {
        'დააპატიმრო': 'სპეც ციხეში ჩასმა',
        'დააპატიმრეთ': 'სპეც ციხეში ჩასმა',
        'დაპატიმრება': 'სპეც ციხეში ჩასმა',
    }

    # Only replace "პატიმრობა" if it's clearly about server punishment
    CONDITIONAL_TRANSLATIONS = {
        'პატიმრობა': 'სპეც ციხე',
        'ციხეში ჩასმა': 'სპეც ციხეში ჩასმა',
        'ციხე': 'სპეც ციხე',
    }

    cursor.execute("SELECT id, question_text, options, correct_answer, explanation, source_type, law_reference FROM quiz_questions")
    all_questions = cursor.fetchall()

    fixed_count = 0
    skipped_ic_count = 0

    for question in all_questions:
        qid, question_text, options_json, correct_answer, explanation, source_type, law_ref = question

        try:
            options = json.loads(options_json)
        except:
            continue

        # Build full context
        full_context = f"{question_text} {options_json} {correct_answer} {explanation} {law_ref}"
        is_ooc = is_ooc_punishment_context(full_context)

        # Skip if clearly IC context
        if is_ooc == False:
            skipped_ic_count += 1
            continue

        needs_update = False
        new_question = question_text
        new_options = options[:]
        new_correct = correct_answer
        new_explanation = explanation

        # Apply always-replace terms
        for old_term, new_term in SMART_TRANSLATIONS.items():
            if old_term in new_question:
                new_question = new_question.replace(old_term, new_term)
                needs_update = True

            if old_term in new_correct:
                new_correct = new_correct.replace(old_term, new_term)
                needs_update = True

            if old_term in new_explanation:
                new_explanation = new_explanation.replace(old_term, new_term)
                needs_update = True

            for i, opt in enumerate(new_options):
                if old_term in opt:
                    new_options[i] = opt.replace(old_term, new_term)
                    needs_update = True

        # Apply conditional terms only if OOC context or source is 'rules'
        if is_ooc or is_ooc is None:
            for old_term, new_term in CONDITIONAL_TRANSLATIONS.items():
                if old_term in new_question:
                    new_question = new_question.replace(old_term, new_term)
                    needs_update = True

                if old_term in new_correct:
                    new_correct = new_correct.replace(old_term, new_term)
                    needs_update = True

                if old_term in new_explanation:
                    new_explanation = new_explanation.replace(old_term, new_term)
                    needs_update = True

                for i, opt in enumerate(new_options):
                    if old_term in opt:
                        new_options[i] = opt.replace(old_term, new_term)
                        needs_update = True

        if needs_update:
            cursor.execute('''
                UPDATE quiz_questions
                SET question_text = ?, options = ?, correct_answer = ?, explanation = ?
                WHERE id = ?
            ''', (new_question, json.dumps(new_options, ensure_ascii=False), new_correct, new_explanation, qid))
            fixed_count += 1
            print(f"Fixed Q{qid} (source: {source_type})")

    conn.commit()
    conn.close()

    print("\n" + "="*80)
    print("SUMMARY:")
    print(f"  Reverted: {reverted_count} questions")
    print(f"  Re-fixed with smart logic: {fixed_count} questions")
    print(f"  Skipped (IC context): {skipped_ic_count} questions")
    print("="*80)

if __name__ == '__main__':
    revert_and_fix_smart()
