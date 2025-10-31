# -*- coding: utf-8 -*-
"""
AI-Powered Quiz Question Generator
Generates quiz questions from Georgian law documents using Gemini AI
"""

import google.generativeai as genai
from config import Config
from law_parser import LawParser
from database import QuizDatabase
import json
import time

class QuizGenerator:
    """Generates quiz questions using AI"""

    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        if self.api_key and self.api_key != "your_gemini_api_key_here":
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
            print("[ERROR] Gemini API key not configured")

        self.law_parser = LawParser()
        self.db = QuizDatabase()

    def generate_questions_from_law(self, law_document, questions_per_law=13):
        """Generate quiz questions from a single law document"""
        if not self.model:
            print("[ERROR] Gemini API not available")
            return []

        # Use optimal text length for reliable generation (10000-12000 chars)
        text_length = min(len(law_document.georgian_text), 12000)

        prompt = f"""თქვენ ხართ საქართველოს პოლიციის ტრენინგ ტესტების გენერატორი.

მოცემული კანონი:
**{law_document.law_name}**

{law_document.georgian_text[:text_length]}

**მიზანი:** შექმენით {questions_per_law} ტესტური კითხვა ამ კანონიდან.

**მოთხოვნები:**

1. შექმენით კითხვები სამი სირთულის დონით:
   - **EASY:** პირდაპირი ფაქტები (რიცხვები, ვადები, სახელები)
   - **MEDIUM:** პროცედურები და გამოყენება
   - **HARD:** სცენარები და რთული შემთხვევები

2. თითოეულ კითხვას უნდა ჰქონდეს:
   - 4 პასუხის ვარიანტი (ქართულად)
   - 1 სწორი პასუხი (უნდა იყოს კანონიდან)
   - 3 არასწორი მაგრამ პლაუზიბელური პასუხი
   - დეტალური ახსნა ზუსტი კანონის ციტატით

3. კატეგორიები:
   - დაკავება (arrest)
   - ჩხრეკა (search)
   - ორდერები (warrants)
   - ტერიტორიები (territories)
   - სასჯელები (penalties)
   - პროცედურები (procedures)
   - უფლებები (rights)

**JSON ფორმატი:**

```json
{{
  "questions": [
    {{
      "question": "კითხვის ტექსტი?",
      "options": ["პასუხი 1", "პასუხი 2", "პასუხი 3", "პასუხი 4"],
      "correct_answer": "სწორი პასუხი",
      "explanation": "ახსნა ციტატით: '{law_document.law_name}, მუხლი X ამბობს: ....'",
      "law_reference": "{law_document.law_name}, მუხლი X",
      "category": "კატეგორია",
      "difficulty": "easy|medium|hard"
    }}
  ]
}}
```

**მაგალითები:**

EASY:
"რამდენ წუთში უნდა წაეკითხოს დაკავებულს მირანდას უფლებები?"

MEDIUM:
"რა უნდა გააკეთოთ თუ სახელმწიფო თანამშრომელი დააკავეთ?"

HARD:
"FIB აგენტს შეუძლია შევიდეს LSPD საკნებში დაკითხვის დროს თუ სპეციალური ორდერი არ აქვს?"

გენერირეთ {questions_per_law} კითხვა. მხოლოდ JSON დააბრუნეთ, დამატებითი ტექსტის გარეშე."""

        max_retries = 2
        for attempt in range(max_retries):
            try:
                print(f"[INFO] Attempt {attempt + 1}/{max_retries}...")

                # Generate with timeout protection
                response = self.model.generate_content(
                    prompt,
                    generation_config={'temperature': 0.7}
                )
                response_text = response.text.strip()

                # Clean up response (remove markdown code blocks if present)
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.startswith('```'):
                    response_text = response_text[3:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]

                response_text = response_text.strip()

                # Parse JSON
                data = json.loads(response_text)
                questions = data.get('questions', [])

                print(f"[INFO] Generated {len(questions)} questions successfully")
                return questions

            except json.JSONDecodeError as e:
                print(f"[ERROR] Failed to parse JSON response: {e}")
                print(f"[DEBUG] Response length: {len(response_text)} chars")
                if attempt < max_retries - 1:
                    print(f"[INFO] Retrying...")
                    time.sleep(3)
                    continue
                return []
            except Exception as e:
                error_msg = str(e)
                if "429" in error_msg or "Resource exhausted" in error_msg:
                    print(f"[ERROR] Rate limit hit on attempt {attempt + 1}")
                    if attempt < max_retries - 1:
                        print(f"[INFO] Waiting 20 seconds before retry...")
                        time.sleep(20)
                        continue
                    else:
                        print(f"[WARN] Skipping law after {max_retries} rate limit attempts")
                        return []
                elif "504" in error_msg or "Deadline" in error_msg:
                    print(f"[ERROR] Timeout on attempt {attempt + 1}: {error_msg}")
                    if attempt < max_retries - 1:
                        print(f"[INFO] Waiting 5 seconds before retry...")
                        time.sleep(5)
                        continue
                    else:
                        print(f"[WARN] Skipping law after {max_retries} timeout attempts")
                        return []
                else:
                    print(f"[ERROR] Failed to generate questions: {error_msg}")
                    return []

        return []

    def generate_all_questions(self, questions_per_law=13):
        """Generate questions from all laws"""
        print("[INFO] Loading laws...")
        self.law_parser.load_all_laws()

        total_generated = 0
        total_laws = len(self.law_parser.laws)
        print(f"[INFO] Will generate {questions_per_law} questions from {total_laws} laws")
        print(f"[INFO] Expected total: ~{questions_per_law * total_laws} questions")

        for idx, law in enumerate(self.law_parser.laws, 1):
            print(f"\n[INFO] Processing law {idx}/{total_laws} (length: {len(law.georgian_text)} chars)")

            questions = self.generate_questions_from_law(law, questions_per_law)

            # Save to database
            for q in questions:
                try:
                    self.db.add_question(q)
                    total_generated += 1
                except Exception as e:
                    print(f"[ERROR] Failed to save question: {str(e)[:100]}")

            print(f"[PROGRESS] Total questions generated so far: {total_generated}")

            # Rate limiting - don't spam Gemini API (10 seconds to avoid 429 errors)
            time.sleep(10)

        print(f"\n[SUCCESS] Generated {total_generated} questions total!")
        print(f"[INFO] Saved to database: {self.db.db_path}")

        return total_generated


if __name__ == "__main__":
    print("="*60)
    print("   Quiz Question Generator")
    print("="*60)

    generator = QuizGenerator()

    print("\nHow many questions per law? (recommended: 3-5)")
    try:
        num = int(input("Enter number: ").strip())
    except:
        num = 3
        print(f"Using default: {num}")

    print(f"\nGenerating {num} questions per law...")
    print("This will take several minutes...\n")

    total = generator.generate_all_questions(questions_per_law=num)

    print("\n" + "="*60)
    print(f"   COMPLETE! Generated {total} questions")
    print("="*60)
