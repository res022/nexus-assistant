# -*- coding: utf-8 -*-
"""
Script to remove old metadata and add new comprehensive metadata to server rules files
"""

import os
import codecs
import json

# Load new metadata
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

    # Remove old metadata if exists
    if '---METADATA---' in content:
        georgian_text = content.split('---METADATA---')[0].strip()
    else:
        georgian_text = content.strip()

    # Get new metadata for this rule
    if rule_key not in metadata:
        print(f"[WARN] No metadata for {filename}")
        continue

    rule_meta = metadata[rule_key]

    # Add new comprehensive metadata
    metadata_text = f"""
---METADATA---
SUMMARY_EN: {rule_meta['summary']}

KEYWORDS_EN: {', '.join(rule_meta['tags'])}"""

    # Write back with new metadata
    new_content = georgian_text + '\n' + metadata_text + '\n'

    with codecs.open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"[OK] Updated metadata for {filename}")

print("\n[DONE] All server rules files updated with comprehensive metadata!")
