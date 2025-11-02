# -*- coding: utf-8 -*-
"""
Remove punishment-related questions from server rules
"""

import sqlite3

def remove_punishment_questions():
    """Remove all punishment/penalty related questions from database"""
    conn = sqlite3.connect('quiz_data.db')
    cursor = conn.cursor()

    # Get count before deletion
    cursor.execute('SELECT COUNT(*) FROM quiz_questions WHERE source_type = "rules"')
    before_count = cursor.fetchone()[0]

    print(f"[INFO] Total rules questions before cleanup: {before_count}")

    # Delete punishment questions based on:
    # - Keywords in question text (სასჯელი, დაჯარიმება, spec jail, BAN, MUTE, warning)
    # - Category = "penalties"
    delete_query = '''
        DELETE FROM quiz_questions
        WHERE source_type = "rules"
        AND (
            question_text LIKE "%სასჯელ%" OR
            question_text LIKE "%დაჯარიმ%" OR
            question_text LIKE "%spec jail%" OR
            question_text LIKE "%BAN%" OR
            question_text LIKE "%MUTE%" OR
            question_text LIKE "%warn%" OR
            question_text LIKE "%გაფრთხილება%" OR
            question_text LIKE "%დასჯ%" OR
            question_text LIKE "%პასუხისმგებლობა%" OR
            category = "penalties"
        )
    '''

    cursor.execute(delete_query)
    deleted_count = cursor.rowcount

    # Get count after deletion
    cursor.execute('SELECT COUNT(*) FROM quiz_questions WHERE source_type = "rules"')
    after_count = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    print(f"[INFO] Deleted {deleted_count} punishment questions")
    print(f"[INFO] Remaining rules questions: {after_count}")
    print(f"[SUCCESS] Cleanup complete!")

if __name__ == '__main__':
    remove_punishment_questions()
