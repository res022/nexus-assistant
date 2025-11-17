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

    def answer_question(self, georgian_question, relevant_laws, context="საქართველოს კანონები"):
        """
        Answer a Georgian question based on relevant laws or rules

        Args:
            georgian_question: User's question in Georgian
            relevant_laws: List of LawDocument/Rule objects (2-5 most relevant)
            context: Context string indicating whether answering about laws or rules

        Returns:
            dict with 'answer' (Georgian text) and 'sources' (list of law/rule names)
        """
        if not self.model:
            return {
                'answer': "❌ Gemini API არ არის კონფიგურირებული. გთხოვთ დააყენოთ API key .env ფაილში.",
                'sources': [],
                'error': True
            }

        if not relevant_laws:
            return {
                'answer': "ბოდიში, ვერ ვიპოვე შესაბამისი დოკუმენტები თქვენი კითხვისთვის.",
                'sources': [],
                'error': False
            }

        try:
            # Build the prompt for Gemini
            prompt = self._build_prompt(georgian_question, relevant_laws, context)

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

    def _build_prompt(self, georgian_question, relevant_laws, context="საქართველოს კანონები"):
        """Build the prompt for Gemini with law/rule context"""

        # Different prompts for laws vs rules
        if "სერვერის წესები" in context:
            # Server rules prompt - ENHANCED for better accuracy
            prompt = """თქვენ ხართ გამოცდილი სერვერის ადმინისტრატორი და როლპლეი ექსპერტი San Andreas Roleplay სერვერისთვის.
თქვენი როლია დაეხმაროთ მოთამაშეებს და ადმინისტრატორებს სწორად გამოიყენონ სერვერის წესები.

**CRITICAL: როგორ უპასუხოთ კითხვებს (გაძლიერებული ინსტრუქციები):**

**ეტაპი 1: კითხვის ᲦᲠᲛᲐ ანალიზი**
   - წაიკითხეთ კითხვა რამდენჯერმე და გაიაზრეთ რა ᲖᲣᲡᲢᲐᲓ გეკითხებიან
   - **"რა არის..." კითხვები** → ეძებეთ DEFINITION/განმარტება სექცია წესებში
   - **"შემიძლია თუ არა..." კითხვები** → ეძებეთ დაშვებულია/აკრძალულია სტატუსი + სასჯელი
   - **"რა ვქნა როცა..." კითხვები** → ეძებეთ პროცედურა და შემდეგი ნაბიჯები
   - **"რა სასჯელია..." კითხვები** → ეძებეთ | BAN/სპეც.ციხე/MUTE/გაფრთხილება ნაწილი

**ეტაპი 2: წესების ᲡᲠᲣᲚᲘ წაკითხვა**
   - წაიკითხეთ ᲗᲘᲗᲝᲔᲣᲚᲘ მოცემული წესი ᲡᲠᲣᲚᲐᲓ, ხაზ-ბა-ხაზ
   - **ᲒᲐᲜᲡᲐᲙᲣᲗᲠᲔᲑᲘᲗ ყურადღება მიაქციეთ:**
     * "განმარტება:" სექციებს (განმარტავს რას ნიშნავს)
     * "შენიშვნა:" სექციებს (დამატებითი დეტალები)
     * "მითითება:" სექციებს (კონკრეტული ინსტრუქციები)
     * "გამონაკლისი:" სექციებს (სპეციალური შემთხვევები)
     * "მაგალითად:" სექციებს (კონკრეტული მაგალითები)
   - იპოვეთ ᲧᲕᲔᲚᲐ რელევანტური ნაწილი წესიდან

**ეტაპი 3: სპეციალური სიტუაციები**

A) **RP ტერმინების გამარტივება (PG, DM, MG, RK, SK, და ა.შ.):**
   - ᲞᲘᲠᲕᲔᲚ ᲠᲘᲒᲨᲘ მოიძიეთ ზოგადი წესები (zogadi.txt) - იქ არის ᲧᲕᲔᲚᲐ ტერმინის განმარტება
   - დაიწყეთ: "**[ტერმინი]** ნიშნავს:"
   - მოკლედ ახსენით რას ნიშნავს (1-2 წინადადება)
   - ᲞᲘᲠᲓᲐᲞᲘᲠ ᲪᲘᲢᲘᲠᲔᲑᲐ წესიდან (" " ნიშნებში)
   - მიუთითეთ სასჯელი (BAN, სპეც.ციხე, MUTE)
   - მაგალითი თუ არის წესებში, ჩართეთ

B) **სასჯელის კითხვები:**
   - იპოვეთ კონკრეტული წესი რომელიც დარღვეულია
   - ᲪᲘᲢᲘᲠᲔᲑᲐ წესის (ნომერით)
   - მიუთითეთ სასჯელი: "| BAN X დღე" ან "| სპეც.ციხე X წუთი" ან "| MUTE X წუთი"
   - თუ არის ინტერვალი (მაგ. "3-14 დღე"), მიუთითეთ რომ დამოკიდებულია დარღვევის სიმძიმეზე

C) **"შემიძლია/შეიძლება" კითხვები:**
   - პასუხი: "✅ დიახ, დაშვებულია" ან "🚫 არა, აკრძალულია"
   - ᲪᲘᲢᲘᲠᲔᲑᲐ წესიდან
   - პირობები თუ არის რაიმე (მაგ. "მხოლოდ თუ...", "გარდა...")
   - განმარტება/შენიშვნა თუ არის

D) **"როგორ ვაკეთო/რა ვქნა" კითხვები:**
   - ჩამოწერეთ ნაბიჯ-ნაბიჯ ინსტრუქციები
   - თითოეულ ნაბიჯს მიამაგრეთ წესის ნომერი
   - მიუთითეთ დრო თუ არის შეზღუდვა
   - გააფრთხილეთ რისი გაკეთება არ შეიძლება

**ეტაპი 4: პასუხის ᲙᲝᲜᲡᲢᲠᲣᲥᲪᲘᲐ**
   - დაიწყეთ მთავარი პასუხით (მაგ. "PG (PowerGaming) ნიშნავს...", "არა, აკრძალულია...", "ამ შემთხვევაში უნდა...")
   - წესის ნომერი (მაგ. "წესი 3.1", "ზოგადი წესები 4.1")
   - ᲞᲘᲠᲓᲐᲞᲘᲠ ᲪᲘᲢᲘᲠᲔᲑᲐ (" " ნიშნებში)
   - განმარტება/შენიშვნა თუ არის
   - სასჯელი თუ არის
   - მაგალითი თუ არის

**ეტაპი 5: ᲓᲐᲓᲐᲡᲢᲣᲠᲔᲑᲐ**
   - შეამოწმეთ: ეხება თუ არა თქვენი პასუხი კითხვას?
   - ნამდვილად იპოვეთ სწორი წესი?
   - არ გამოგრჩათ სასჯელი?
   - თუ ვერ პოულობთ, უთხარით "ვერ ვიპოვე ამის შესახებ ინფორმაცია წესებში"

**ფორმატირება:**
   - 🚫 აკრძალულია
   - ✅ დაშვებულია/სავალდებულოა
   - ⏱️ ვადები/დრო
   - ⚠️ სასჯელები
   - 📋 პირობები

**პასუხობთ მხოლოდ ქართულ ენაზე. იყავით კონკრეტული და ზუსტი.**"""
        else:
            # Georgian laws prompt - ENHANCED for better accuracy
            prompt = """თქვენ ხართ გამოცდილი იურიდიული ასისტენტი სან ანდრეასის შტატის პოლიციისთვის და პროკურატურისთვის.
თქვენი როლია დაეხმაროთ ოფიცრებს სწორად გამოიყენონ კანონები პრაქტიკაში.

**CRITICAL: როგორ უპასუხოთ კითხვებს (გაძლიერებული ინსტრუქციები):**

**ეტაპი 1: კითხვის ᲦᲠᲛᲐ ანალიზი (დაუთმეთ დრო!)**
   - წაიკითხეთ კითხვა რამდენჯერმე და გაიაზრეთ რა ᲖᲣᲡᲢᲐᲓ გეკითხებიან
   - არ აურიოთ მსგავსი მაგრამ განსხვავებული ცნებები:
     * "შეურაცხყოფა" (insult/disrespect) ≠ "თავდასხმა" (attack/assault)
     * "დაკავება" (arrest) ≠ "დაკითხვა" (interrogation)
     * "ჩხრეკა" (search) ≠ "შემოსვლა" (entry)
   - გამოყავით კითხვის მთავარი თემა და კონტექსტი
   - თუ კითხვა არის სიტუაციური (მაგ. "გავაკეთე X, ახლა რა ვქნა?"), იპოვეთ სწორედ იმ სიტუაციის შემდეგი ნაბიჯები

**ეტაპი 2: კანონების ᲡᲠᲣᲚᲘ და ᲧᲣᲠᲐᲓᲦᲔᲑᲘᲗ წაკითხვა**
   - წაიკითხეთ ᲗᲘᲗᲝᲔᲣᲚᲘ მოცემული კანონის ტექსტი ᲡᲠᲣᲚᲐᲓ, ხაზ-ბა-ხაზ
   - ნუ გამოტოვებთ არცერთ მუხლს, არცერთ ნაწილს
   - იპოვეთ ᲖᲣᲡᲢᲘ მუხლი რომელიც პასუხობს კითხვას
   - იპოვეთ ᲧᲕᲔᲚᲐ რელევანტური ნაწილი რომელიც ეხება კითხვას
   - არ გამოტოვოთ არცერთი მნიშვნელოვანი დეტალი

**ეტაპი 3: პასუხის ᲡᲠᲣᲚᲘ ᲙᲝᲜᲡᲢᲠᲣᲥᲪᲘᲐ**
   - დაიწყეთ მთავარი პასუხით (მაგ. "დიახ, შეგიძლიათ" ან "არა, არ შეგიძლიათ")
   - დაასახელეთ კონკრეტული კანონი და მუხლის ნომერი
   - ᲞᲘᲠᲓᲐᲞᲘᲠ ᲪᲘᲢᲘᲠᲔᲑᲐ გააკეთეთ რელევანტური ნაწილის (" " ნიშნებში)
   - თუ კითხვა არის "რა ვქნა შემდეგ?", მიუთითეთ კონკრეტული ნაბიჯები
   - ნუ დაამატებთ ზედმეტ ინფორმაციას თუ არ გეკითხებიან

**ეტაპი 4: პასუხის ᲓᲐᲓᲐᲡᲢᲣᲠᲔᲑᲐ**
   - კიდევ ერთხელ შეამოწმეთ: ეხება თუ არა თქვენი პასუხი კითხვას?
   - დარწმუნდით რომ არ გამოგრჩათ მნიშვნელოვანი დეტალები
   - თუ ვერ პოულობთ პასუხს, უთხარით "ვერ ვიპოვე ამის შესახებ ინფორმაცია კანონებში"

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
        Use hybrid approach: keyword matching + AI selection for better accuracy
        Returns list of selected law/rule documents
        """
        if not self.model:
            return all_laws[:max_laws]  # Fallback: return first few laws

        try:
            # STEP 1: Pre-filter with keyword matching (hybrid approach)
            keyword_matches = self._keyword_prefilter(georgian_question, all_laws)

            # If keyword matching found strong matches, use those + AI selection
            if len(keyword_matches) >= 3:
                # Use keyword matches as priority, then fill with AI selection
                candidate_pool = keyword_matches[:max_laws * 2]  # Top keyword matches
                print(f"[INFO] Keyword pre-filter found {len(keyword_matches)} matches, using top {len(candidate_pool)} as candidates")
            else:
                # Not enough keyword matches, use all documents
                candidate_pool = all_laws
                print(f"[INFO] Keyword pre-filter found {len(keyword_matches)} matches, using all {len(candidate_pool)} documents")

            # STEP 2: AI selection from candidate pool
            # Create a detailed list of documents with full summaries and keywords
            laws_list = []
            for i, law in enumerate(candidate_pool, 1):
                # Include FULL summary and keywords for better selection
                summary_full = law.summary_en if law.summary_en else "No summary"
                keywords_full = law.keywords_en if hasattr(law, 'keywords_en') and law.keywords_en else "No keywords"
                english_title = getattr(law, 'english_title', 'N/A')

                laws_list.append(f"{i}. {law.filename} | {english_title}\n   Georgian Title: {law.law_name[:100]}\n   Summary: {summary_full}\n   Keywords: {keywords_full}\n")

            laws_text = "\n".join(laws_list)

            prompt = f"""You are a legal/rules assistant for San Andreas State (Georgia-based GTA roleplay server).

Given this Georgian legal question:
"{georgian_question}"

Select the {max_laws} MOST RELEVANT laws/rules from this list that would help answer the question.

**SELECTION INSTRUCTIONS:**
1. Read the question carefully and identify the main topic/keywords
2. Match the question against the Summary and Keywords provided for each document
3. Prioritize documents where the Summary or Keywords contain terms related to the question
4. Use the English summaries and keywords to understand what each document covers
5. Select documents that directly contain information to answer the question

**AVAILABLE DOCUMENTS:**

{laws_text}

**CRITICAL SELECTION RULES:**

**For LAWS (laws/ directory):**
- "ორდერი/ორდერ" (warrant) → dokumentebis.txt
- "დაკავების ორდერი/AW" (arrest warrant) → dokumentebis.txt
- "გუბერნატორი" (governor) + warrants → dokumentebis.txt + mtavrob.txt
- "პროკურორი/პროკურატურა" (prosecutor) → prokuraturis.txt
- "პოლიცია/LSPD/ოფიცერი" (police/officer) → policiis.txt
- "დაკავება/დააკავოს" (arrest) → saproceso.txt
- "იარაღი" (weapon) → sisxlissamartali.txt + iaragis.txt
- "ბრონი/ჟილეტი" (armor/vest) → sisxlissamartali.txt
- "ადვოკატი" (lawyer) → saproceso.txt + saadvokato.txt
- "რამდენი ხანი/ვადა" (how long/timeframe) → saproceso.txt
- "საკნები/საკანი/ჩასვლა საკნებში" (cells/cell access) → teritoriebis.txt
- "FIB access/ჩასვლა" (FIB access) → teritoriebis.txt
- "ტერიტორია/ზონა/წითელი ზონა" (territory/zone) → teritoriebis.txt
- "დანაშაული/სასჯელი/ისჯება" (crime/penalty) → sisxlissamartali.txt
- "შეურაცხყოფა" (insult) → sisxlissamartali.txt
- "თავდასხმა" (attack/assault) → sisxlissamartali.txt

**For SERVER RULES (serverrules/ directory):**
- "რა არის PG/DM/MG/RK/SK/BU/TK/AR/PA/NRD/DB/CR/SP" (what is [RP term]) → zogadi.txt (has ALL definitions)
- "PowerGaming/MetaGaming/DeathMatch/Fear RP" → zogadi.txt
- "ანგარიში/მულტი-აქაუნთ" (account/multi-account) → zogadi.txt
- "ბიზნესი/business ownership" → zogadi.txt
- "ნიღაბი/mask" (mask requirement) → zogadi.txt
- "/me /do /try commands" → zogadi.txt
- "ადმინი/admin rules" → administraciis.txt
- "პოლიცია/cop/LSPD/FIB/USSS/NG/EMS rules" → saxelmwifoorganizaciis.txt
- "NonRP COP" → saxelmwifoorganizaciis.txt
- "ბანდა/gang/მაფია/mafia" → kriminaluriorganizaciebis.txt
- "მასალები/faction storage" → kriminaluriorganizaciebis.txt
- "ჩხრეკა/რობერი/გატაცება/kidnap" → dzarcvagataceba.txt
- "EMS/news immunity" → dzarcvagataceba.txt
- "ლიდერი/leader" → lideriswesebi.txt
- "rank editing/კიკი/kick" → lideriswesebi.txt
- "ოჯახი/family" → ojaxis.txt
- "green zone/red zone/ზონა" → satamashozonebi.txt
- "პოლიგრაფი/polygraph/lie detector" → poligrafis.txt
- "სროლა/shooting/combat" → rpstreli.txt
- "heal/revive during fight" → rpstreli.txt
- "ჩხრეკა/search/frisk" → rpgamodzieba.txt
- "ტერიტორია/territory war" → teritoriebzeomi.txt
- "რეიდი/raid" → reidis.txt
- "graffiti/spray" → grafitiwar.txt
- "airdrop" → airdrop.txt
- "supplies/მომარაგება" → momarageba.txt
- "VZH/wanted/hostage" → vzh.txt
- "Fort Zancudo/military base" → fortzacundo.txt
- "Weazel News journalist" → weazelnews.txt
- "terrorist/terror act" → teroristuliaqtis.txt
- "FCK/faction conflict" → fck.txt
- "soft check/anticheat" → softcheck.txt

**SELECTION STRATEGY:**
1. First check if question matches any keyword patterns above
2. Then carefully read Summary and Keywords for each document
3. Select documents where Summary DIRECTLY addresses the question
4. Prioritize documents with matching keywords in the Keywords field
5. Return the {max_laws} MOST RELEVANT documents

Return ONLY the numbers of the selected documents, separated by commas (e.g., "1,5,12,3,7").
Choose documents that DIRECTLY contain information to answer the question."""

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

    def _keyword_prefilter(self, georgian_question, all_documents):
        """
        Pre-filter documents using keyword matching for better accuracy
        Returns list of documents sorted by relevance score
        """
        question_lower = georgian_question.lower()

        # Enhanced keyword mapping with common Georgian terms
        keyword_patterns = {
            # Laws keywords
            'ორდერ': ['dokumentebis', 'warrant', 'order'],
            'დაკავება': ['saproceso', 'arrest', 'detention'],
            'პროკურორ': ['prokuraturis', 'prosecutor'],
            'პოლიცი': ['policiis', 'police'],
            'იარაღ': ['sisxlissamartali', 'iaragis', 'weapon', 'firearm'],
            'ბრონ': ['sisxlissamartali', 'armor'],
            'ჟილეტ': ['sisxlissamartali', 'vest'],
            'ადვოკატ': ['saproceso', 'saadvokato', 'lawyer', 'attorney'],
            'საკან': ['teritoriebis', 'cell'],
            'საკნებ': ['teritoriebis', 'cell'],
            'ტერიტორი': ['teritoriebis', 'territory'],
            'ზონა': ['teritoriebis', 'satamashozonebi', 'zone'],
            'დანაშაულ': ['sisxlissamartali', 'crime'],
            'სასჯელ': ['sisxlissamartali', 'penalty'],
            'შეურაცხყოფ': ['sisxlissamartali', 'insult'],
            'თავდასხმ': ['sisxlissamartali', 'attack', 'assault'],

            # Server rules keywords
            'pg': ['zogadi', 'powergaming'],
            'dm': ['zogadi', 'deathmatch'],
            'mg': ['zogadi', 'metagaming'],
            'fear rp': ['zogadi', 'fear'],
            'rk': ['zogadi', 'revenge kill'],
            'sk': ['zogadi', 'spawn kill'],
            'რა არის': ['zogadi', 'definition'],  # "what is" - likely RP term question
            'ანგარიშ': ['zogadi', 'account'],
            'ბიზნეს': ['zogadi', 'business'],
            'ნიღაბ': ['zogadi', 'kriminaluriorganizaciebis', 'mask'],
            '/me': ['zogadi', 'command'],
            '/do': ['zogadi', 'command'],
            '/try': ['zogadi', 'command'],
            'ადმინ': ['administraciis', 'admin'],
            'ბანდ': ['kriminaluriorganizaciebis', 'gang'],
            'მაფი': ['kriminaluriorganizaciebis', 'mafia'],
            'მასალებ': ['kriminaluriorganizaciebis', 'momarageba', 'materials', 'supplies'],
            'ძარცვ': ['dzarcvagataceba', 'robbery'],
            'გატაცებ': ['dzarcvagataceba', 'kidnap'],
            'ლიდერ': ['lideriswesebi', 'leader'],
            'კიკ': ['lideriswesebi', 'kick'],
            'ოჯახ': ['ojaxis', 'family'],
            'green zone': ['satamashozonebi', 'green zone'],
            'red zone': ['satamashozonebi', 'red zone'],
            'პოლიგრაფ': ['poligrafis', 'polygraph'],
            'სროლ': ['rpstreli', 'shooting'],
            'ჩხრეკ': ['rpgamodzieba', 'dzarcvagataceba', 'search'],
            'რეიდ': ['reidis', 'raid'],
            'graffiti': ['grafitiwar', 'graffiti'],
            'airdrop': ['airdrop'],
            'vzh': ['vzh', 'wanted'],
            'fort zancudo': ['fortzacundo', 'military'],
            'weazel': ['weazelnews', 'news'],
            'terrorist': ['teroristuliaqtis', 'terror'],
            'fck': ['fck', 'faction conflict'],
            'soft check': ['softcheck', 'anticheat'],
            'lspd': ['policiis', 'saxelmwifoorganizaciebis', 'police'],
            'fib': ['saxelmwifoorganizaciebis', 'federal'],
            'ems': ['saxelmwifoorganizaciebis', 'dzarcvagataceba', 'medical'],
        }

        # Score each document
        document_scores = []
        for doc in all_documents:
            score = 0

            # Check Georgian question against patterns
            for pattern, related_terms in keyword_patterns.items():
                if pattern in question_lower:
                    # Check if any related term appears in document filename, keywords, or summary
                    doc_text = f"{doc.filename} {doc.keywords_en} {doc.summary_en}".lower()
                    for term in related_terms:
                        if term in doc_text:
                            score += 3  # High score for pattern match

            # Also check direct keyword matching in document metadata
            if hasattr(doc, 'keywords_en') and doc.keywords_en:
                doc_keywords_lower = doc.keywords_en.lower()
                # Check for Georgian terms in question that might be in English keywords
                for word in question_lower.split():
                    if len(word) > 3:  # Ignore very short words
                        # Check if any keyword patterns match
                        for pattern in keyword_patterns:
                            if pattern in word:
                                # Look for related English terms in keywords
                                for related in keyword_patterns[pattern]:
                                    if related in doc_keywords_lower:
                                        score += 2

            # Check summary match
            if hasattr(doc, 'summary_en') and doc.summary_en:
                summary_lower = doc.summary_en.lower()
                # Look for English equivalents of Georgian terms
                for pattern, related_terms in keyword_patterns.items():
                    if pattern in question_lower:
                        for term in related_terms:
                            if term in summary_lower:
                                score += 1

            if score > 0:
                document_scores.append((doc, score))

        # Sort by score descending
        document_scores.sort(key=lambda x: x[1], reverse=True)

        # Return documents only (without scores)
        return [doc for doc, score in document_scores]
