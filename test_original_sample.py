#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import find_all_rhymes

# Original sample text from the web interface
original_text = """Tripping off the beat kinda, dripping off the meat grinder
Heat niner, pimping, stripping, soft sweet minor
China was a neat signer, trouble with the script
The magnificent different president, evident hesitant"""

print("=== TESTING ORIGINAL SAMPLE WITH NEW ALGORITHM ===\n")

result = find_all_rhymes(original_text)

print(f"Found {len(result['rhyme_groups'])} rhyme groups:")
print()

for group_key, group_info in result['rhyme_groups'].items():
    words_in_group = [w['clean'] for w in group_info['words']]
    rhyme_type = group_info.get('rhyme_type', 'unknown')
    group_letter = group_info.get('letter', '?')
    pattern = group_info.get('pattern', 'unknown')

    print(f"Group {group_letter} ({rhyme_type}): {len(words_in_group)} words")
    print(f"  Pattern: {pattern}")
    print(f"  Words: {', '.join(words_in_group)}")
    print()

print("Lines with analysis:")
for i, line in enumerate(result['lines']):
    print(f"{i+1}: {line}")