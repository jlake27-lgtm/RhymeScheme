#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import find_all_rhymes
import pronouncing

# Your comprehensive -est rhymes test
est_rhymes = """abreast, abscessed, accessed, acquest, addressed, addrest, addwest, adpressed, aggressed, agreste, aleste, all-dressed, altfest, angest, appressed, armrest, arrest, arzest, asbest, assessed, ateste, attest, at best, at rest, av-test, backrest, bankwest, bedrest, behest, bench-pressed, bequest, bird's nest, blood-test, bluebreast, bookrest, breath-test, bud-test, canwest, caressed, carquest, celest, celeste, charest, chin rest, compressed, confessed, confest, congest, contest, conteste, crash-test, cross-dressed, crow's nest, d'allest, depressed, detest, devest, digest, digressed, distressed, divest, due west, east-west, egressed, elfquest, excessed, expressed, farwest, ferrest, field-test, fieldcrest, finessed, finevest, flight-test, fluoresced, flyquest, fowl pest, funeste, funfest, get dressed, goldcrest, grundfest, gun rest, had best, hamfest, hard-pressed, hardpressed, headrest, healthvest, high-test, holmquest, hope chest, hotpressed, house guest, hyndreste, ice chest, ill-dressed, impressed, incest, increst, infest, ingest, inquest, invest, jeanswest, key west, knotfest, life vest, low-test, mae west, magfest, male chest, mapquest, mare's nest, marquest, means-test, mechquest, midwest, modeste, molest, moogfest, mouse nest, nape-crest, natwest, newsquest, north-west, northwest, norwest, obsessed, obssessed, oppressed, outbreast, outfest, outguessed, outwrest, penwest, pix chest, possessed, pre-test, precessed, prestressed, pretest, professed, progressed, proquest, protest, quiesced, recessed, redbreast, redressed, regressed, repressed, request, retest, rhymefest, ridgecrest, road-test, saw-wrest, screen-test, sealtest, seaquest, sea chest, segrest, self-test, sinfest, skywest, slop chest, slugfest, songfest, south-west, southwest, stateswest, steam chest, sub-test, sudeste, suggest, suppressed, swordquest, sylvest, tea chest, techfest, tin pest, tool-rest, tool chest, top-dressed, toy chest, transgressed, transvest, trivest, turnwrest, unblessed, unblest, unbreast, undressed, unguessed, unpressed, unrest, unstressed, volksfest, war chest, wasp's nest, webquest, well-dressed, whole rest, wild west, woodcrest"""

print("=== DEBUGGING -EST RHYMES ===\n")

# First, let's check what the pronouncing library says about these
test_words = [word.strip() for word in est_rhymes.split(',')]
print(f"Total words to test: {len(test_words)}")

# Check how many have phonetic data
words_with_phones = []
words_without_phones = []
rhyme_parts = {}

for word in test_words[:20]:  # Test first 20 words
    clean_word = word.lower().replace('-', ' ').strip()

    # Try different variations
    variations = [
        clean_word,
        clean_word.replace(' ', ''),  # Remove spaces
        clean_word.split()[-1] if ' ' in clean_word else clean_word  # Last word only
    ]

    found_phones = False
    for variant in variations:
        phones = pronouncing.phones_for_word(variant)
        if phones:
            rhyme_part = pronouncing.rhyming_part(phones[0])
            rhyme_parts[word] = rhyme_part
            words_with_phones.append(word)
            print(f"✓ {word:20} -> {variant:15} -> {phones[0]:25} -> {rhyme_part}")
            found_phones = True
            break

    if not found_phones:
        words_without_phones.append(word)
        print(f"✗ {word:20} -> NO PHONETIC DATA")

print(f"\nPhonetic data found for: {len(words_with_phones)}/{len(test_words[:20])}")
print(f"Missing phonetic data: {len(words_without_phones)}")

# Check rhyme part consistency
if rhyme_parts:
    print(f"\nRhyme parts analysis:")
    unique_rhyme_parts = set(rhyme_parts.values())
    print(f"Unique rhyme parts found: {len(unique_rhyme_parts)}")
    for part in unique_rhyme_parts:
        words_with_part = [w for w, p in rhyme_parts.items() if p == part]
        print(f"  {part}: {len(words_with_part)} words")

# Now test our algorithm
print(f"\n=== TESTING OUR ALGORITHM ===")
result = find_all_rhymes(est_rhymes)
print(f"Our algorithm found {len(result['rhyme_groups'])} groups:")

for group_key, group_info in result['rhyme_groups'].items():
    words_in_group = [w['clean'] for w in group_info['words']]
    rhyme_type = group_info.get('rhyme_type', 'unknown')
    group_letter = group_info.get('letter', '?')
    print(f"Group {group_letter} ({rhyme_type}): {len(words_in_group)} words")
    if len(words_in_group) <= 10:
        print(f"  Words: {', '.join(words_in_group[:10])}")
    else:
        print(f"  First 10: {', '.join(words_in_group[:10])}")