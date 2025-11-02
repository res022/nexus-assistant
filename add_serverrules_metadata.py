# -*- coding: utf-8 -*-
"""
Script to add metadata to server rules files
"""

import os
import codecs
import json

# Load metadata
with codecs.open('serverrules_metadata.json', 'r', encoding='utf-8') as f:
    metadata = json.load(f)

# Process each server rules file
rules_dir = 'serverrules'
for filename in os.listdir(rules_dir):
    if not filename.endswith('.txt'):
        continue

    filepath = os.path.join(rules_dir, filename)
    rule_key = filename.replace('.txt', '')

    # Read current content
    with codecs.open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if metadata already exists
    if '---METADATA---' in content:
        print(f"[SKIP] {filename} already has metadata")
        continue

    # Get metadata for this rule
    if rule_key not in metadata:
        print(f"[WARN] No metadata for {filename}")
        continue

    rule_meta = metadata[rule_key]

    # Add metadata
    metadata_text = f"""
---METADATA---
SUMMARY_EN: {rule_meta['summary']}

KEYWORDS_EN: {', '.join(rule_meta['tags'])}"""

    # Write back with metadata
    new_content = content.strip() + '\n' + metadata_text + '\n'

    with codecs.open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"[OK] Added metadata to {filename}")

print("\n[DONE] Metadata added to all server rules files!")
