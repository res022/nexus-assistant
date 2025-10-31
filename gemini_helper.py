# -*- coding: utf-8 -*-
"""
Gemini API Helper - Handles Google Gemini API interactions for law questions
"""

import google.generativeai as genai
from config import Config
import time

class GeminiHelper:
    """Helper class for Google Gemini API integration"""

    def __init__(self, api_key=None):
        """Initialize Gemini API"""
        self.api_key = api_key or Config.GEMINI_API_KEY
        
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            print("[WARN] Gemini API key not configured. Set GEMINI_API_KEY in .env file")
            self.model = None
        else:
            try:
                genai.configure(api_key=self.api_key)
                # Use the latest stable Gemini 2.0 Flash model (fast and free)
                model_name = 'gemini-2.0-flash'
                self.model = genai.GenerativeModel(model_name)
                print(f"[INFO] Gemini API initialized successfully with model: {model_name}")
            except Exception as e:
                print(f"[ERROR] Failed to initialize Gemini API: {str(e)}")
                self.model = None

    def answer_question(self, georgian_question, relevant_laws):
        """
        Answer a Georgian question based on relevant laws
        
        Args:
            georgian_question: User's question in Georgian
            relevant_laws: List of LawDocument objects (2-5 most relevant)
        
        Returns:
            dict with 'answer' (Georgian text) and 'sources' (list of law names)
        """
        if not self.model:
            return {
                'answer': "❌ Gemini API არ არის კონფიგურირებული. გთხოვთ დააყენოთ API key .env ფაილში.",
                'sources': [],
                'error': True
            }

        if not relevant_laws:
            return {
                'answer': "ბოდიში, ვერ ვიპოვე შესაბამისი კანონები თქვენი კითხვისთვის.",
                'sources': [],
                'error': False
            }

        try:
            # Build the prompt for Gemini
            prompt = self._build_prompt(georgian_question, relevant_laws)
            
            # Call Gemini API
            response = self.model.generate_content(prompt)
            
            # Extract answer
            answer_text = response.text.strip()
            
            # Extract sources
            sources = [law.law_name for law in relevant_laws]
            
            return {
                'answer': answer_text,
                'sources': sources,
                'error': False
            }

        except Exception as e:
            error_msg = str(e)
            # Avoid printing Georgian text to console to prevent encoding errors
            print(f"[ERROR] Gemini API call failed: {error_msg}")
            return {
                'answer': f"❌ შეცდომა AI-ს პასუხის გენერირებისას: {error_msg}",
                'sources': [],
                'error': True
            }

    def _build_prompt(self, georgian_question, relevant_laws):
        """Build the prompt for Gemini with law context"""
        
        prompt = """თქვენ ხართ გამოცდილი იურიდიული ასისტენტი სან ანდრეასის შტატის პოლიციისთვის და პროკურატურისთვის.
თქვენი როლია დაეხმაროთ ოფიცრებს სწორად გამოიყენონ კანონები პრაქტიკაში.

**CRITICAL: როგორ უპასუხოთ კითხვებს:**

1. **ᲞᲘᲠᲕᲔᲚᲘ, გაიაზრეთ კითხვა ზუსტად:**
   - წაიკითხეთ კითხვა ᲧᲣᲠᲐᲓᲦᲔᲑᲘᲗ და გაიაზრეთ რა ᲖᲣᲡᲢᲐᲓ გეკითხებიან
   - არ აურიოთ მსგავსი მაგრამ განსხვავებული ცნებები:
     * "შეურაცხყოფა" (insult/disrespect) ≠ "თავდასხმა" (attack/assault)
     * "დაკავება" (arrest) ≠ "დაკითხვა" (interrogation)
     * "ჩხრეკა" (search) ≠ "შემოსვლა" (entry)
   - თუ კითხვა არის "შეურაცხყოფა", მოძებნეთ სწორედ "შეურაცხყოფის" შესახებ, არა "თავდასხმის" შესახებ
   - თუ ვერ პოულობთ ზუსტ პასუხს, უთხარით მომხმარებელს რომ ვერ იპოვეთ, არ მისცეთ არასწორი პასუხი

2. **მეორე, მოძებნეთ ზუსტი მუხლი:**
   - წაიკითხეთ კანონების ტექსტი ᲡᲠᲣᲚᲐᲓ და ყურადღებით
   - იპოვეთ ᲖᲣᲡᲢᲘ მუხლი რომელიც პასუხობს კითხვას
   - დარწმუნდით რომ მუხლი პასუხობს სწორედ იმას რაც კითხულობენ
   - არ გამოტოვოთ არცერთი მნიშვნელოვანი დეტალი კანონში

3. **გააცით ᲛᲝᲙᲚᲔ და ᲙᲝᲜᲙᲠᲔᲢᲣᲚᲘ პასუხი:**
   - დაიწყეთ მთავარი პასუხით (მაგ. "დიახ, შეგიძლიათ" ან "არა, არ შეგიძლიათ")
   - დაასახელეთ კონკრეტული კანონი და მუხლის ნომერი
   - ᲞᲘᲠᲓᲐᲞᲘᲠ ᲪᲘᲢᲘᲠᲔᲑᲐ გააკეთეთ რელევანტური ნაწილის (" " ნიშნებში)
   - ნუ დაამატებთ ზედმეტ ინფორმაციას თუ არ გეკითხებიან

4. **თუ კითხვა არის "როდის შემიძლია...":**
   - უპასუხეთ კონკრეტულად რა პირობებში შეიძლება
   - ციტირეთ ზუსტი პირობები კანონიდან
   - არ ჩამოთვალოთ ყველა შესაძლო სცენარი თუ არ გეკითხებიან

5. **თუ კითხვა პროცედურის შესახებ ("რა გავაკეთო როდესაც..."):**
   - ჩამოთვალეთ ნაბიჯები
   - თითოეულ ნაბიჯს მიამაგრეთ კონკრეტული მუხლი
   - იყავით კონკრეტული და ლაკონური

6. **⚠️ გამოავლინეთ ᲙᲠᲘᲢᲘᲙᲣᲚᲘ მოთხოვნები:**
   - თუ კანონში არის ვადები (მაგ. "3 წუთის განმავლობაში"), მონიშნეთ ⏱️ ემოჯით
   - თუ საჭიროა სპეციალური ნებართვა/ორდერი, მონიშნეთ 📋 ემოჯით
   - თუ რაიმე აკრძალულია, მონიშნეთ 🚫 ემოჯით
   - თუ სავალდებულოა რაიმე (მაგ. მირანდას უფლებები), მონიშნეთ ✅ ემოჯით

7. **🔗 ჩართეთ ᲙᲐᲕᲨᲘᲠᲔᲑᲘ სხვა კანონებთან:**
   - თუ პასუხი დაკავშირებულია სხვა კანონებთან, მოკლედ აღნიშნეთ
   - მაგალითი: "იხილეთ ასევე: საპროცესო კოდექსი, მუხლი X"

8. **🚫 ნუ დაამატებთ ზედმეტ ინფორმაციას:**
   - ᲐᲠᲐᲡᲝᲓᲔᲡ დაამატოთ "დამატებით:" სექცია
   - ᲐᲠᲐᲡᲝᲓᲔᲡ დაამატოთ "შემდეგი ნაბიჯები:" ან "დაკავშირებული კითხვები:" სექციები
   - მიეცით მხოლოდ ის ინფორმაცია რაც პირდაპირ არის კანონში ნაწერი
   - თავიდან აიცილეთ დამატებითი ახსნა-განმარტებები რომელიც კანონში არ არის
   - პასუხი უნდა შეიცავდეს მხოლოდ კანონის პირდაპირ ციტატებს და ახსნას

9. **პასუხობთ მხოლოდ ქართულ ენაზე**

**მაგალითი სწორი, ᲛᲝᲙᲚᲔ პასუხისა:**
კითხვა: "როდის შემიძლია FIB თანამშრომელს საკნებთან ჩასვლა?"

სწორი პასუხი (მოკლე და ზუსტი):
"FIB თანამშრომელს შეუძლია საკნებთან ჩასვლა შემდეგ შემთხვევებში:

**კანონი დახურული და დაცული ტერიტორიების შესახებ, მუხლი 6.1.2** ამბობს:

'LSPD საკნების ტერიტორია არის წითელი ზონა, ტერიტორიაზე დაიშვება:
ა) LSPD, USSS, NG, FIB თანამშრომლები დაკავების, დაკავებულთა გადაცემის, დაკითხვის დროს ან სპეციალური ორდერით/ნებართვით.'

**შესაბამისად, FIB-ს შეუძლია:**
✅ დაკავების დროს
✅ დაკავებულთა გადაცემისას
✅ დაკითხვის დროს
📋 სპეციალური ორდერით/ნებართვით"

**არასწორი პასუხი (ძალიან გრძელი და ზედმეტი ინფორმაციით):**
"პირველ რიგში უნდა გავიაზროთ რა არის საკანი და რატომ არის ის დაცული... [3 პარაგრაფი ზოგადი ინფორმაციის შესახებ]... ასევე უნდა გვახსოვდეს რომ პოლიციასაც აქვს უფლება... [კიდევ 2 პარაგრაფი]..."

---

**მოცემული კანონები:**

"""
        # Add each law with its summary and full text
        for idx, law in enumerate(relevant_laws, 1):
            prompt += f"\n### კანონი #{idx}: {law.law_name}\n"
            prompt += f"**Summary (English):** {law.summary_en}\n\n"
            prompt += f"**სრული ტექსტი (ქართული):**\n{law.georgian_text[:50000]}\n"  # Increased to 50000 chars - should cover entire law documents
            prompt += "\n" + "="*80 + "\n"

        prompt += f"""
---

**მომხმარებლის კითხვა (ქართული):**
{georgian_question}

**თქვენი პასუხი (ქართული):**
"""

        return prompt

    def translate_to_english(self, georgian_text):
        """
        Translate Georgian text to English for keyword extraction
        This is optional and can be used if simple keyword matching isn't enough
        """
        if not self.model:
            return ""

        try:
            prompt = f"""Translate the following Georgian text to English. 
Only provide the translation, no explanations:

{georgian_text}

English translation:"""

            response = self.model.generate_content(prompt)
            return response.text.strip()

        except Exception as e:
            print(f"[ERROR] Translation failed: {str(e)}")
            return ""

    def select_relevant_laws(self, georgian_question, all_laws, max_laws=5):
        """
        Use Gemini to intelligently select the most relevant laws for a question
        Returns list of selected law filenames
        """
        if not self.model:
            return all_laws[:max_laws]  # Fallback: return first few laws

        try:
            # Create a compact list of laws with their titles and summaries
            laws_list = []
            for i, law in enumerate(all_laws, 1):
                laws_list.append(f"{i}. {law.filename} - {law.law_name[:50]}... (EN: {law.summary_en[:100]}...)")

            laws_text = "\n".join(laws_list)

            prompt = f"""You are a legal assistant for San Andreas State (Georgia-based roleplay server).

Given this Georgian legal question:
"{georgian_question}"

Select the {max_laws} MOST RELEVANT laws from this list that would help answer the question:

{laws_text}

**CRITICAL KEYWORD MATCHING RULES:**
- Questions about "ორდერი/ორდერ" (warrant/order) → MUST include "dokumentebis.txt" (contains AR, SA, FB, AW, FW, IW warrant types)
- Questions about "დაკავების ორდერი" or "AW" (arrest warrant) → MUST include "dokumentebis.txt"
- Questions about "გუბერნატორი" (governor) powers + warrants → MUST include "dokumentebis.txt" AND "mtavrob.txt"
- Questions about "პროკურორი/პროკურატურა/გენერალური პროკურორი" (prosecutor/attorney general) → prioritize "prokuraturis.txt"
- Questions about "პოლიცია/LSPD/ოფიცერი" (police/officer) → prioritize "policiis.txt"
- Questions about "დაკავება/დააკავოს" (arrest/detention) procedures → prioritize "saproceso.txt"
- Questions about "იარაღი" (weapon/firearm) → prioritize "sisxlissamartali.txt" AND "iaragis.txt"
- Questions about "ბრონი/ჟილეტი" (armor/vest) → MUST include "sisxlissamartali.txt"
- Questions about "ადვოკატი/ადვოკატის უფლება" (lawyer/attorney) → prioritize "saproceso.txt" AND "saadvokato.txt"
- Questions about "რამდენი ხანი/ვადა/წუთი" (how long/timeframe/minutes) → prioritize "saproceso.txt"
- Questions about "საკნები/საკანი/ჩასვლა საკნებში/საკნებთან" (cells/cell access/entering cells) → MUST include "teritoriebis.txt"
- Questions about "FIB/ფედერალური ბიურო" access to cells or territories → MUST include "teritoriebis.txt"
- Questions about "ტერიტორია/დახურული/დაცული/ზონა/წითელი ზონა" (territory/closed/protected/zone/red zone) → MUST include "teritoriebis.txt"
- Questions about who can enter specific locations (LSPD cells, FIB territory, etc.) → MUST include "teritoriebis.txt"
- Questions about crimes/penalties: "ისჯება/სასჯელი/დანაშაული/შეურაცხყოფა/თავდასხმა" (punished/penalty/crime/insult/attack) → MUST include "sisxlissamartali.txt"
- Questions about "შეურაცხყოფა" (insult/disrespect) → MUST include "sisxlissamartali.txt" (NOT same as "თავდასხმა" attack)

Return ONLY the numbers of the selected laws, separated by commas (e.g., "1,5,12,3,7").
Choose laws that directly contain information about the question's topic."""

            response = self.model.generate_content(prompt)
            selected_numbers = response.text.strip()

            # Parse the selected numbers
            try:
                numbers = [int(n.strip()) - 1 for n in selected_numbers.split(',') if n.strip().isdigit()]
                selected_laws = [all_laws[i] for i in numbers if 0 <= i < len(all_laws)]

                if selected_laws:
                    print(f"[INFO] Gemini selected {len(selected_laws)} laws")
                    return selected_laws[:max_laws]
            except Exception as parse_error:
                print(f"[WARN] Failed to parse Gemini selection: {parse_error}")

            # Fallback if parsing fails
            return all_laws[:max_laws]

        except Exception as e:
            print(f"[ERROR] Law selection failed: {str(e)}")
            return all_laws[:max_laws]

    def extract_keywords_from_question(self, georgian_question):
        """
        Use Gemini to extract English keywords from a Georgian question
        This is more accurate than manual mapping
        """
        if not self.model:
            return ['law', 'legal']  # Default fallback

        try:
            prompt = f"""Extract 3-5 English keywords from this Georgian legal question.
Return only the keywords separated by commas, nothing else.

Georgian question: {georgian_question}

English keywords:"""

            response = self.model.generate_content(prompt)
            keywords_text = response.text.strip()
            keywords = [kw.strip().lower() for kw in keywords_text.split(',')]

            return keywords[:5]  # Max 5 keywords

        except Exception as e:
            print(f"[ERROR] Keyword extraction failed: {str(e)}")
            return ['law', 'legal']  # Default fallback
