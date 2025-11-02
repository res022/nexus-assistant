# -*- coding: utf-8 -*-
import sqlite3
import codecs
import sys

# Fix console encoding
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

conn = sqlite3.connect('quiz_data.db')
cursor = conn.cursor()

# Check all unique categories
cursor.execute('SELECT DISTINCT category, source_type, COUNT(*) FROM quiz_questions GROUP BY category, source_type ORDER BY source_type, COUNT(*) DESC')
results = cursor.fetchall()

print("\n=== ALL CATEGORIES ===")
for row in results:
    cat_display = row[0][:25] if len(row[0]) > 25 else row[0]
    print(f"{row[1]:10} | {cat_display:25} | {row[2]:4} questions")

# Check for penalty-related categories
cursor.execute('SELECT COUNT(*) FROM quiz_questions WHERE category LIKE "%penalty%" OR category LIKE "%penalties%"')
penalty_count = cursor.fetchone()[0]
print(f"\n\nEnglish penalty categories found: {penalty_count}")

# Count by source
cursor.execute('SELECT source_type, COUNT(*) FROM quiz_questions GROUP BY source_type')
sources = cursor.fetchall()
print("\n=== TOTALS BY SOURCE ===")
for s in sources:
    print(f"{s[0]}: {s[1]} questions")

conn.close()
