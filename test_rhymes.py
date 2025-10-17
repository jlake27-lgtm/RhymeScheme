#!/usr/bin/env python3

import pronouncing

# Test list from user
test_words = [
    "rest", "best", "beste", "blessed", "blest", "breast", "brest", "breste",
    "cessed", "ceste", "chesed", "chest", "chrest", "cresst", "crest", "dest",
    "deste", "dressed", "drest", "este", "f-test", "fessed", "fest", "feste",
    "flest", "g-test", "gest", "geste", "guessed", "guest", "jessed", "jest",
    "lest", "leste", "messed", "mest", "nest", "neste", "pest", "peste",
    "pressed", "prest", "quest", "queste", "rest", "reste", "stressed", "teste",
    "threst", "threste", "tressed", "trest", "v-test", "vest", "veste", "west",
    "weste", "wrest", "yessed", "yest", "yoest", "z-test", "zest", "zeste"
]

print("=== RHYME DETECTION TEST ===\n")

# Remove duplicates and sort
unique_words = sorted(list(set(test_words)))
print(f"Testing {len(unique_words)} unique words:")
print(", ".join(unique_words))
print()

# Test which words have phonetic representations
words_with_phones = []
words_without_phones = []

for word in unique_words:
    phones = pronouncing.phones_for_word(word)
    if phones:
        words_with_phones.append(word)
        print(f"✓ {word}: {phones[0]}")
    else:
        words_without_phones.append(word)
        print(f"✗ {word}: NO PHONETIC DATA")

print(f"\n=== SUMMARY ===")
print(f"Words with phonetic data: {len(words_with_phones)}/{len(unique_words)} ({len(words_with_phones)/len(unique_words)*100:.1f}%)")
print(f"Words WITHOUT phonetic data: {len(words_without_phones)}")

if words_without_phones:
    print(f"\nMissing phonetic data for: {', '.join(words_without_phones)}")

# Test rhyming between known words
print(f"\n=== RHYME TESTING ===")
base_word = "test"
if base_word in words_with_phones:
    rhymes_with_test = pronouncing.rhymes(base_word)
    print(f"Words that rhyme with '{base_word}' according to pronouncing library:")

    found_in_our_list = []
    for word in words_with_phones:
        if word in rhymes_with_test:
            found_in_our_list.append(word)

    print(f"Found {len(found_in_our_list)} matches: {', '.join(sorted(found_in_our_list))}")

    # Check what we're missing
    missing = [w for w in words_with_phones if w not in rhymes_with_test and w != base_word]
    if missing:
        print(f"Words in our list NOT detected as rhymes: {', '.join(sorted(missing))}")

        # Check their rhyming parts
        print(f"\nRhyming part analysis:")
        test_rhyme_part = pronouncing.rhyming_part(pronouncing.phones_for_word(base_word)[0])
        print(f"'{base_word}' rhyming part: {test_rhyme_part}")

        for word in missing[:5]:  # Check first 5 missing words
            phones = pronouncing.phones_for_word(word)
            if phones:
                rhyme_part = pronouncing.rhyming_part(phones[0])
                match = "✓" if rhyme_part == test_rhyme_part else "✗"
                print(f"{match} '{word}' rhyming part: {rhyme_part}")