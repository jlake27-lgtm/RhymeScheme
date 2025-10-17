#!/usr/bin/env python3
"""Test the refined rhyme system"""

from app import word_to_syllables, create_syllables_from_phonetics, compare_syllables
import pronouncing

def test_system():
    print("=== TESTING REFINED RHYME SYSTEM ===\n")

    # Test words that should rhyme on the -ent ending
    test_words = ["magnificent", "different", "president", "evident", "hesitant"]

    print("1. Testing word to syllables conversion:")
    for word in test_words:
        syllables = word_to_syllables(word, word)
        print(f"  {word}: {syllables}")

    print("\n2. Testing syllable creation from phonetics:")
    all_syllables = []
    for word in test_words:
        phones = pronouncing.phones_for_word(word)
        if phones:
            syllables = create_syllables_from_phonetics(word, phones[0])
            all_syllables.extend(syllables)
            syllable_strs = [f"{s['syllable']}({s['rhyme_part']})" for s in syllables]
            print(f"  {word}: {syllable_strs}")
        else:
            print(f"  {word}: NO PHONETIC DATA")

    print(f"\n3. Total syllables created: {len(all_syllables)}")

    print("\n4. Testing syllable comparison:")
    similar_pairs = []
    for i, syl1 in enumerate(all_syllables):
        for j, syl2 in enumerate(all_syllables[i+1:], i+1):
            score = compare_syllables(syl1, syl2)
            if score > 0.5:  # Our threshold
                similar_pairs.append((syl1, syl2, score))

    print(f"  Found {len(similar_pairs)} similar syllable pairs:")
    for syl1, syl2, score in similar_pairs:
        print(f"    {syl1['syllable']} ({syl1['rhyme_part']}) <-> {syl2['syllable']} ({syl2['rhyme_part']}) = {score:.2f}")

    print("\n5. Testing simple rhyme fallback:")
    for word in test_words:
        rhymes = pronouncing.rhymes(word)
        found_rhymes = [w for w in test_words if w in rhymes and w != word]
        print(f"  {word} rhymes with: {found_rhymes}")

if __name__ == "__main__":
    test_system()