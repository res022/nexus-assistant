# -*- coding: utf-8 -*-
"""
Server Rules Parser - Load and parse GTA5 roleplay server rules
"""

import os
import codecs
import json


class ServerRulesParser:
    """Parse server rules from serverrules/ directory"""

    def __init__(self, rules_dir='serverrules', metadata_file='serverrules_metadata.json'):
        self.rules_dir = rules_dir
        self.metadata_file = metadata_file
        self.rules = []
        self.metadata = {}

    def load_metadata(self):
        """Load English metadata for server rules"""
        if os.path.exists(self.metadata_file):
            with codecs.open(self.metadata_file, 'r', encoding='utf-8') as f:
                self.metadata = json.load(f)
        else:
            print(f"[WARN] Metadata file not found: {self.metadata_file}")
        return self.metadata

    def parse_all_rules(self):
        """Parse all server rules files with metadata integration"""
        if not os.path.exists(self.rules_dir):
            print(f"[WARNING] Server rules directory not found: {self.rules_dir}")
            return []

        # Load metadata first
        self.load_metadata()

        files = sorted([f for f in os.listdir(self.rules_dir) if f.endswith('.txt')])

        for filename in files:
            try:
                rule_data = self.parse_rule_file(filename)
                if rule_data:
                    self.rules.append(rule_data)
            except Exception as e:
                print(f"[ERROR] Failed to parse {filename}: {str(e)}")

        print(f"[INFO] Loaded {len(self.rules)} server rules with metadata")
        return self.rules

    def parse_rule_file(self, filename):
        """Parse a single server rules file and integrate metadata from JSON"""
        filepath = os.path.join(self.rules_dir, filename)

        with codecs.open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Remove the ---METADATA--- section if it exists (we use JSON metadata instead)
        if '---METADATA---' in content:
            content = content.split('---METADATA---')[0].strip()

        # Extract title (first line)
        lines = content.split('\n')
        title = lines[0].strip() if lines else filename.replace('.txt', '').replace('_', ' ').title()

        # Get metadata from JSON file using filename without extension as key
        file_key = filename.replace('.txt', '')
        metadata_entry = self.metadata.get(file_key, {})

        # Extract metadata fields
        summary_en = metadata_entry.get('summary', '')
        keywords_en = ', '.join(metadata_entry.get('tags', []))  # Join tags into keywords string
        english_title = metadata_entry.get('english_title', '')
        category = metadata_entry.get('category', 'Rules')

        return {
            'filename': filename,
            'title': title,
            'content': content,  # Georgian text without metadata
            'summary_en': summary_en,
            'keywords_en': keywords_en,
            'english_title': english_title,
            'category': category
        }

    def get_rule_by_filename(self, filename):
        """Get a specific rule by filename"""
        for rule in self.rules:
            if rule['filename'] == filename:
                return rule
        return None

    def search_rules(self, query):
        """Search rules by query string"""
        query_lower = query.lower()
        results = []

        for rule in self.rules:
            if (query_lower in rule['title'].lower() or
                query_lower in rule['content'].lower() or
                query_lower in rule.get('english_title', '').lower() or
                query_lower in rule.get('summary', '').lower()):
                results.append(rule)

        return results

    def get_all_rules_text(self):
        """Get all server rules as one combined text"""
        all_text = "=== ᲡᲔᲠᲕᲔᲠᲘᲡ ᲬᲔᲡᲔᲑᲘ (SERVER RULES) ===\n\n"

        for rule in self.rules:
            all_text += f"━━━ {rule['title']} ━━━\n"
            if rule.get('english_title'):
                all_text += f"English: {rule['english_title']}\n"
            if rule.get('summary'):
                all_text += f"Summary: {rule['summary']}\n"
            all_text += f"\n{rule['content']}\n\n"
            all_text += "=" * 80 + "\n\n"

        return all_text

    def get_rules_by_category(self, category):
        """Get rules filtered by category"""
        return [r for r in self.rules if r.get('category', '').lower() == category.lower()]


if __name__ == '__main__':
    parser = ServerRulesParser()
    parser.load_metadata()
    rules = parser.parse_all_rules()

    print(f"\nLoaded {len(rules)} server rules:")
    for rule in rules:
        print(f"  - {rule['filename']} ({len(rule['content'])} chars)")
