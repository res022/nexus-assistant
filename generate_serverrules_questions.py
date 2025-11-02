# -*- coding: utf-8 -*-
"""
AI-Powered Server Rules Quiz Question Generator
Generates 300 quiz questions from Georgian server rules using Gemini AI
"""

import google.generativeai as genai
from config import Config
from serverrules_parser import ServerRulesParser
from database import QuizDatabase
import json
import time

class ServerRulesQuizGenerator:
    """Generates quiz questions from server rules using AI"""

    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
            print("[ERROR] Gemini API key not configured")

        self.rules_parser = ServerRulesParser()
        self.db = QuizDatabase()

    def generate_questions_from_rule(self, rule_data, questions_per_rule=13):
        """Generate quiz questions from a single server rule file"""
        if not self.model:
            print("[ERROR] Gemini API not available")
            return []

        # Use optimal text length for reliable generation
        text_length = min(len(rule_data['content']), 12000)

        prompt = f"""თქვენ ხართ San Andreas Roleplay სერვერის წესების ტესტების გენერატორი.

მოცემული წესი:
**{rule_data['title']}**

{rule_data['content'][:text_length]}

**მიზანი:** შექმენით {questions_per_rule} პრაქტიკული ტესტური კითხვა ამ წესიდან.

**მნიშვნელოვანი:** კითხვები უნდა იყოს პრაქტიკული და გამოსადეგი:
- რა არის PG/DM/MG და სხვა RP ტერმინები?
- როდის შეიძლება VZH/SZ გამოყენება?
- რამდენი კითხვა პოლიგრაფზე?
- რა არის კონკრეტული წესის მოთხოვნები?
- როგორ მუშაობს კონკრეტული მექანიკა/სისტემა?

**აკრძალულია:**
- სასჯელების შესახებ კითხვები (spec jail, BAN, MUTE, გაფრთხილება)
- დარღვევების პასუხისმგებლობის შესახებ
- DeMorgan's laws, logic theory, abstract concepts, programming concepts

**მოთხოვნები:**

1. შექმენით კითხვები სამი სირთულის დონით:
   - **EASY:** ტერმინების განმარტება, რიცხვები, ვადები, სახელები
   - **MEDIUM:** პროცედურები, წესების გამოყენება, დასაშვები მოქმედებები
   - **HARD:** სცენარები, რთული შემთხვევები, გადაწყვეტილებები

2. თითოეულ კითხვას უნდა ჰქონდეს:
   - 4 პასუხის ვარიანტი (ქართულად)
   - 1 სწორი პასუხი (უნდა იყოს წესიდან)
   - 3 არასწორი მაგრამ პლაუზიბელური პასუხი
   - დეტალური ახსნა ზუსტი წესის ციტატით

3. კატეგორიები (არ გამოიყენო "penalties"):
   - rp_definitions (RP ტერმინები: PG, DM, MG, Fear RP და ა.შ.)
   - admin_rules (ადმინისტრაციის წესები - არა სასჯელები!)
   - faction_rules (ფრაქციების წესები)
   - event_rules (ღონისძიებების წესები)
   - combat_rules (შებრძოლების წესები: VZH, SZ, RP სტრელა და ა.შ.)
   - procedures (პროცედურები: პოლიგრაფი, დაკითხვა, რეიდი და ა.შ.)
   - general_rules (ზოგადი წესები: ანგარიში, კომუნიკაცია და ა.შ.)
   - mechanics (მექანიკები და სისტემები)

**JSON ფორმატი:**

```json
{{
  "questions": [
    {{
      "question": "კითხვის ტექსტი?",
      "options": ["პასუხი 1", "პასუხი 2", "პასუხი 3", "პასუხი 4"],
      "correct_answer": "სწორი პასუხი",
      "explanation": "ახსნა ციტატით: '{rule_data['title']}, წესი X.X ამბობს: ....'",
      "law_reference": "{rule_data['title']}, წესი X.X",
      "category": "კატეგორია",
      "difficulty": "easy|medium|hard"
    }}
  ]
}}
```

**მაგალითები კითხვებისა (არ ვითხოვოთ სასჯელების შესახებ!):**

EASY:
"რა არის PG (PowerGaming)?"
"რამდენი ოფიციალური შეკითხვა შეიძლება დავსვა პოლიგრაფზე?"
"რა არის DM (Death Match)?"
"რომელ ზონებში აკრძალულია დანაშაული?"

MEDIUM:
"როდის შეიძლება VZH-ს გამოყენება?"
"როგორ უნდა გათამაშდეს /try პოლიგრაფის შემთხვევაში?"
"რა წესები აქვს ფრაქციის ლიდერს ფაქციის მართვისას?"
"რა პროცედურა აქვს რეიდს?"

HARD:
"მოთამაშემ დაიწყო სროლა VZH სიტუაციაში. PG-ად ჩაითვლება თუ არა?"
"SZ-ზე PG დაშვებულია თუ აკრძალულია?"
"ლიდერმა გაათავისუფლა წევრი IC მიზეზის გარეშე. რა წესი დაარღვია?"

გენერირეთ {questions_per_rule} კითხვა. მხოლოდ JSON დააბრუნეთ, დამატებითი ტექსტის გარეშე."""

        max_retries = 2
        for attempt in range(max_retries):
            try:
                print(f"[INFO] Generating {questions_per_rule} questions from {rule_data['filename']} (attempt {attempt + 1})...")
                response = self.model.generate_content(prompt)
                result_text = response.text.strip()

                # Clean JSON response
                if '```json' in result_text:
                    result_text = result_text.split('```json')[1].split('```')[0].strip()
                elif '```' in result_text:
                    result_text = result_text.split('```')[1].split('```')[0].strip()

                result = json.loads(result_text)
                questions = result.get('questions', [])

                if questions and len(questions) > 0:
                    print(f"[SUCCESS] Generated {len(questions)} questions from {rule_data['filename']}")
                    return questions
                else:
                    print(f"[WARN] No questions generated on attempt {attempt + 1}")

            except Exception as e:
                print(f"[ERROR] Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                continue

        print(f"[ERROR] Failed to generate questions from {rule_data['filename']} after {max_retries} attempts")
        return []

    def save_questions_to_db(self, questions, source_type='rules'):
        """Save generated questions to database"""
        saved_count = 0
        for q in questions:
            try:
                question_data = {
                    'question': q['question'],
                    'options': q['options'],
                    'correct_answer': q['correct_answer'],
                    'explanation': q['explanation'],
                    'law_reference': q['law_reference'],
                    'category': q['category'],
                    'difficulty': q['difficulty'],
                    'source_type': source_type
                }
                self.db.add_question(question_data)
                saved_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to save question: {str(e)}")

        return saved_count

def main():
    """Generate 300 server rules quiz questions"""
    generator = ServerRulesQuizGenerator()

    # Load all server rules
    generator.rules_parser.parse_all_rules()
    all_rules = generator.rules_parser.rules

    print(f"\n[INFO] Starting server rules quiz generation...")
    print(f"[INFO] Total server rules files: {len(all_rules)}")
    print(f"[INFO] Target: 300 questions (~13-14 per file)\n")

    total_generated = 0
    total_saved = 0

    # Generate ~13-14 questions per file to reach 300 total
    questions_per_file = 14

    for idx, rule in enumerate(all_rules, 1):
        print(f"\n{'='*80}")
        print(f"Processing {idx}/{len(all_rules)}: {rule['filename']}")
        print(f"{'='*80}")

        questions = generator.generate_questions_from_rule(rule, questions_per_file)
        total_generated += len(questions)

        if questions:
            saved = generator.save_questions_to_db(questions, source_type='rules')
            total_saved += saved
            print(f"[INFO] Saved {saved}/{len(questions)} questions to database")

        print(f"[INFO] Progress: {total_saved}/300 questions saved")

        # Rate limiting
        if idx < len(all_rules):
            print("[INFO] Waiting 10 seconds before next file...")
            time.sleep(10)

    print(f"\n{'='*80}")
    print(f"[DONE] Server Rules Quiz Generation Complete!")
    print(f"{'='*80}")
    print(f"Total generated: {total_generated} questions")
    print(f"Total saved: {total_saved} questions")
    print(f"Success rate: {(total_saved/total_generated*100) if total_generated > 0 else 0:.1f}%")

if __name__ == '__main__':
    main()
