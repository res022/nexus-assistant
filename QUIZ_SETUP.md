# Quiz Mode Setup Guide

## Overview
AI-generated quiz system that creates smart questions from Georgian law documents.

## Setup Steps

### 1. Generate Questions

Run the question generator to create quiz questions from all law documents:

```bash
python quiz_generator.py
```

**Prompts:**
- Enter how many questions per law (recommended: 3-5)
- Script will process all laws and generate questions
- Questions are saved to `quiz_data.db`

**What it does:**
- AI reads each law document
- Generates questions at 3 difficulty levels (easy/medium/hard)
- Creates 4 multiple-choice options per question
- Includes explanations with law citations
- Categories: დაკავება, ჩხრეკა, ორდერები, ტერიტორიები, სასჯელები, etc.

**Example output:**
```
Processing: კანონი დახურული და დაცული ტერიტორიების შესახებ
Generated 5 questions from კანონი დახურული და დაცული...
...
COMPLETE! Generated 150 questions
```

### 2. Start the Application

```bash
python app.py
```

### 3. Access Quiz Mode

Open browser: `http://localhost:5000/quiz`

## Features

### Quiz Options
- 5 questions (quick)
- 10 questions (standard)
- 15 questions (long)
- 20 questions (full)

### Smart Features
- **Mixed Difficulty:** Random questions from easy, medium, hard
- **Mixed Topics:** Questions across all law categories
- **Instant Feedback:** Shows correct answer and explanation after each question
- **Progress Tracking:** Tracks performance by category
- **Statistics:** Overall accuracy, questions answered, performance by topic

### Question Format

**Easy Example:**
```
Q: რამდენ წუთში უნდა წაეკითხოს დაკავებულს მირანდას უფლებები?
A) 1 წუთი
B) 3 წუთი ✓
C) 5 წუთი
D) 10 წუთი

Explanation: საპროცესო კოდექსი, მუხლი 3.1 ამბობს: "დაკავებულს უნდა წაეკითხოს მისი უფლებები 3 წუთის განმავლობაში"
```

**Medium Example:**
```
Q: რა უნდა გააკეთოთ თუ სახელმწიფო თანამშრომელი დააკავეთ?
```

**Hard Example:**
```
Q: FIB აგენტს შეუძლია შევიდეს LSPD საკნებში დაკითხვის დროს თუ სპეციალური ორდერი არ აქვს?
```

## Database Schema

### quiz_questions
- question_text
- options (JSON array)
- correct_answer
- explanation
- law_reference
- category
- difficulty (easy/medium/hard)

### quiz_history
- Tracks user answers
- Records correct/incorrect
- Stores session data

### user_progress
- Overall statistics
- Performance by category

## Customization

### Generate More Questions

Run generator again to add more questions:
```bash
python quiz_generator.py
```

### Categories

Current categories:
- დაკავება (arrest)
- ჩხრეკა (search)
- ორდერები (warrants)
- ტერიტორიები (territories)
- სასჯელები (penalties)
- პროცედურები (procedures)
- უფლებები (rights)

## Troubleshooting

**No questions available:**
- Run `python quiz_generator.py` to generate questions
- Check that `quiz_data.db` exists

**Gemini API Error:**
- Verify `GEMINI_API_KEY` in `.env` file
- Check internet connection

**Questions not appearing:**
- Check database: `quiz_db.get_question_count()`
- Verify questions are approved: `is_approved = 1`

## Future Enhancements

Planned features:
- Adaptive difficulty (adjusts based on performance)
- Spaced repetition
- Topic selection
- Time pressure mode
- Leaderboards
- Daily challenges
