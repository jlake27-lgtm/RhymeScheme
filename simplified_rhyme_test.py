#!/usr/bin/env python3

import pronouncing
import re

def normalize_rhyme_part(rhyme_part):
    """Normalize rhyme parts by removing stress markers for comparison"""
    if not rhyme_part:
        return ""
    phonemes = rhyme_part.split()
    normalized = []
    for phoneme in phonemes:
        clean_phoneme = re.sub(r'[0-2]', '', phoneme)
        normalized.append(clean_phoneme)
    return ' '.join(normalized)

def clean_word(word):
    """Clean word for processing"""
    if ' ' in word:
        parts = word.strip().split()
        if len(parts) >= 2:
            word = parts[-1]  # Take the last word

    if '-' in word:
        parts = word.split('-')
        if len(parts) == 2 and parts[1]:
            word = parts[1]

    return re.sub(r'[^\w]', '', word.lower())

# Test with a smaller set first
test_words = ["best", "test", "rest", "west", "nest", "guest", "chest", "pressed", "dressed", "blessed"]

print("=== SIMPLIFIED RHYME TEST ===")

# Group words by their normalized rhyme parts
rhyme_groups = {}

for word in test_words:
    clean = clean_word(word)
    phones = pronouncing.phones_for_word(clean)

    if phones:
        rhyme_part = pronouncing.rhyming_part(phones[0])
        normalized = normalize_rhyme_part(rhyme_part)

        if normalized not in rhyme_groups:
            rhyme_groups[normalized] = []
        rhyme_groups[normalized].append(clean)

        print(f"{clean:10} -> {phones[0]:20} -> {rhyme_part:10} -> {normalized}")
    else:
        print(f"{clean:10} -> NO PHONETIC DATA")

print(f"\nFound {len(rhyme_groups)} normalized rhyme groups:")
for norm_pattern, words in rhyme_groups.items():
    print(f"'{norm_pattern}': {words}")