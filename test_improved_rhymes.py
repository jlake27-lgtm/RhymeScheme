#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import find_all_rhymes

# Test the improved rhyme detection with your problematic list
test_text = """rest best beste blessed blest breast brest breste
cessed ceste chesed chest chrest cresst crest dest
deste dressed drest este f-test fessed fest feste
flest g-test gest geste guessed guest jessed jest
lest leste messed mest nest neste pest peste
pressed prest quest queste rest reste stressed teste
threst threste tressed trest v-test vest veste west
weste wrest yessed yest yoest z-test zest zeste"""

print("=== IMPROVED RHYME DETECTION TEST ===\n")

# Analyze the text
result = find_all_rhymes(test_text)

print(f"Found {len(result['rhyme_groups'])} rhyme groups:")
print()

for group_key, group_info in result['rhyme_groups'].items():
    words_in_group = [w['clean'] for w in group_info['words']]
    rhyme_type = group_info.get('rhyme_type', 'unknown')
    group_letter = group_info.get('letter', '?')

    print(f"Group {group_letter} ({rhyme_type}): {', '.join(words_in_group)}")

print(f"\nTotal words found in rhyme groups: {sum(len(group['words']) for group in result['rhyme_groups'].values())}")

# Count words that weren't grouped
all_words = []
for line in result['lines']:
    words = line.split()
    for word in words:
        clean = word.lower().strip('.,!?;:"()[]{}')
        if len(clean) >= 2:
            all_words.append(clean)

words_in_groups = set()
for group in result['rhyme_groups'].values():
    for word_obj in group['words']:
        words_in_groups.add(word_obj['clean'])

ungrouped_words = [w for w in set(all_words) if w not in words_in_groups]
print(f"Words not in any rhyme group: {', '.join(sorted(ungrouped_words))}")