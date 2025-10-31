# -*- coding: utf-8 -*-
"""
Law Parser - Reads and parses Georgian law files with English metadata
"""

import os
import codecs
from config import Config

class LawDocument:
    """Represents a single law document"""

    def __init__(self, filename, law_name, georgian_text, summary_en, keywords_en):
        self.filename = filename
        self.law_name = law_name  # First line of the file (Georgian title)
        self.georgian_text = georgian_text  # Full Georgian text
        self.summary_en = summary_en  # English summary from metadata
        self.keywords_en = keywords_en  # English keywords from metadata

    def __repr__(self):
        return f"<LawDocument: {self.law_name[:50]}...>"

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'filename': self.filename,
            'law_name': self.law_name,
            'georgian_text': self.georgian_text,
            'summary_en': self.summary_en,
            'keywords_en': self.keywords_en
        }


class LawParser:
    """Parser for Georgian law files with English metadata"""

    def __init__(self, laws_directory=None):
        self.laws_directory = laws_directory or Config.LAWS_DIRECTORY
        self.laws = []

    def parse_file(self, filepath):
        """Parse a single law file"""
        try:
            with codecs.open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Split into Georgian text and metadata
            if Config.METADATA_SEPARATOR in content:
                parts = content.split(Config.METADATA_SEPARATOR)
                georgian_text = parts[0].strip()
                metadata_section = parts[1].strip()
            else:
                # No metadata found - skip or handle gracefully
                print(f"[WARN] No metadata found in {os.path.basename(filepath)}")
                georgian_text = content.strip()
                metadata_section = ""

            # Extract law name (first line)
            lines = georgian_text.split('\n')
            law_name = lines[0].strip() if lines else "Untitled Law"

            # Parse metadata
            summary_en = ""
            keywords_en = ""

            if metadata_section:
                for line in metadata_section.split('\n'):
                    if line.startswith('SUMMARY_EN:'):
                        summary_en = line.replace('SUMMARY_EN:', '').strip()
                    elif line.startswith('KEYWORDS_EN:'):
                        keywords_en = line.replace('KEYWORDS_EN:', '').strip()

            return LawDocument(
                filename=os.path.basename(filepath),
                law_name=law_name,
                georgian_text=georgian_text,
                summary_en=summary_en,
                keywords_en=keywords_en
            )

        except Exception as e:
            print(f"[ERROR] Failed to parse {filepath}: {str(e)}")
            return None

    def load_all_laws(self):
        """Load all law files from the directory"""
        self.laws = []

        if not os.path.exists(self.laws_directory):
            print(f"[ERROR] Laws directory not found: {self.laws_directory}")
            return []

        for filename in sorted(os.listdir(self.laws_directory)):
            if filename.endswith('.txt'):
                filepath = os.path.join(self.laws_directory, filename)
                law_doc = self.parse_file(filepath)
                if law_doc:
                    self.laws.append(law_doc)

        print(f"[INFO] Loaded {len(self.laws)} law documents")
        return self.laws

    def get_law_by_filename(self, filename):
        """Get a specific law by filename"""
        for law in self.laws:
            if law.filename == filename:
                return law
        return None

    def search_by_english_keywords(self, query_keywords, max_results=5):
        """
        Search laws by matching English keywords and summaries
        Returns the most relevant laws based on keyword matching
        """
        query_keywords_lower = [kw.strip().lower() for kw in query_keywords]

        matches = []

        for law in self.laws:
            score = 0

            # Search in keywords
            law_keywords = [kw.strip().lower() for kw in law.keywords_en.split(',')]
            for query_kw in query_keywords_lower:
                for law_kw in law_keywords:
                    if query_kw in law_kw or law_kw in query_kw:
                        score += 2  # Keywords are weighted higher

            # Search in summary
            summary_lower = law.summary_en.lower()
            for query_kw in query_keywords_lower:
                if query_kw in summary_lower:
                    score += 1

            if score > 0:
                matches.append((law, score))

        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)

        # Return top matches
        return [law for law, score in matches[:max_results]]

    def search_in_georgian_text(self, query, max_results=5):
        """
        Search directly in Georgian law text
        Returns laws that contain words from the query
        """
        # Extract significant words from query (ignore very short words)
        query_words = [word.strip().lower() for word in query.split() if len(word.strip()) > 2]

        if not query_words:
            return []

        matches = []

        for law in self.laws:
            score = 0
            law_text_lower = law.georgian_text.lower()

            # Count how many query words appear in the law text
            for word in query_words:
                # Count occurrences of this word
                count = law_text_lower.count(word)
                if count > 0:
                    score += count

            if score > 0:
                matches.append((law, score))

        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)

        # Return top matches
        return [law for law, score in matches[:max_results]]

    def extract_keywords_from_georgian_text(self, georgian_question):
        """
        Extract potential keywords from Georgian question
        This is a simple implementation - can be enhanced with NLP
        """
        # Common keywords that might appear in questions
        keyword_mapping = {
            'პროკურატურა': 'prosecutor',
            'პროკურორი': 'prosecutor',
            'პოლიცია': 'police',
            'სასამართლო': 'court',
            'იარაღი': 'firearm',
            'მართვის': 'driving',
            'სიჩქარე': 'speed',
            'პარკინგი': 'parking',
            'დაკავება': 'arrest',
            'ჩხრეკა': 'search',
            'უფლება': 'rights',
            'მედია': 'media',
            'ჟურნალისტი': 'journalism',
            'ტერორიზმი': 'terrorism',
            'დანაშაული': 'crime',
            'სისხლის': 'criminal',
            'ჯარიმა': 'fine',
            'შეზღუდული': 'restricted',
            'იმუნიტეტი': 'immunity'
        }

        # Extract keywords
        keywords = []
        question_lower = georgian_question.lower()

        for georgian, english in keyword_mapping.items():
            if georgian in question_lower:
                keywords.append(english)

        return keywords if keywords else ['law', 'legal']  # Default fallback
