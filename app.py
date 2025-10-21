from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re
import pronouncing

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/analyze', methods=['POST'])
def analyze_rhyme_scheme():
    try:
        data = request.get_json()
        text = data.get('text', '')
        if not text:
            return jsonify({'error': 'No text provided'}), 400

        analysis = find_all_rhymes(text)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

def clean_word(word):
    """Remove punctuation and convert to lowercase"""
    if ' ' in word:
        parts = word.strip().split()
        if len(parts) >= 2:
            word = parts[-1]  # Take the last word for phrases

    if '-' in word:
        parts = word.split('-')
        if len(parts) == 2 and parts[1]:
            word = parts[1]  # Take part after hyphen

    return re.sub(r'[^\w]', '', word.lower())

def phonetic_similarity(phones1, phones2, threshold=0.7):
    """Calculate phonetic similarity between two phoneme sequences"""
    if not phones1 or not phones2:
        return 0.0

    # Get rhyming parts (suffix similarity is most important for rhymes)
    rhyme1 = pronouncing.rhyming_part(phones1)
    rhyme2 = pronouncing.rhyming_part(phones2)

    if not rhyme1 or not rhyme2:
        return 0.0

    # Split into phonemes
    phonemes1 = rhyme1.split()
    phonemes2 = rhyme2.split()

    # Calculate similarity score based on matching phonemes
    if len(phonemes1) == 0 or len(phonemes2) == 0:
        return 0.0

    # For exact matches
    if rhyme1 == rhyme2:
        return 1.0

    # For near-matches, check phoneme overlap
    common_phonemes = 0
    max_len = max(len(phonemes1), len(phonemes2))
    min_len = min(len(phonemes1), len(phonemes2))

    # Check overlap from the end (most important for rhymes)
    for i in range(min_len):
        if phonemes1[-(i+1)] == phonemes2[-(i+1)]:
            common_phonemes += 1
        else:
            break

    # Calculate similarity score
    similarity = common_phonemes / max_len

    # Special cases for known slant rhymes
    slant_rhyme_patterns = [
        # -ing variations (pimping/tripping)
        (['IH1', 'M', 'P', 'IH0', 'NG'], ['IH1', 'P', 'IH0', 'NG']),
        # -er variations (grinder/miner)
        (['AY1', 'N', 'D', 'ER0'], ['AY1', 'N', 'ER0']),
        # -uble variations (subtle/trouble)
        (['AH1', 'T', 'AH0', 'L'], ['AH1', 'B', 'AH0', 'L'])
    ]

    for pattern1, pattern2 in slant_rhyme_patterns:
        if (phonemes1 == pattern1 and phonemes2 == pattern2) or \
           (phonemes1 == pattern2 and phonemes2 == pattern1):
            similarity = 0.8  # High similarity for known slant rhymes

    return similarity

def find_all_rhymes(text):
    """Enhanced rhyme detection with phonetic similarity"""
    lines = text.split('\n')
    all_words = []

    # Step 1: Extract all words with positions and phonetic data
    for line_idx, line in enumerate(lines):
        words = line.split()
        for word_idx, word in enumerate(words):
            clean = clean_word(word)
            if len(clean) >= 2:
                phones = pronouncing.phones_for_word(clean)
                all_words.append({
                    'original': word,
                    'clean': clean,
                    'line_index': line_idx,
                    'word_index': word_idx,
                    'phones': phones[0] if phones else None
                })

    # Step 2: Find rhyme groups using enhanced detection
    rhyme_groups = []
    used_words = set()
    group_counter = 0
    colors = [
        '#C0392B', '#138D75', '#1F618D', '#27AE60', '#F39C12', '#8E44AD',
        '#E74C3C', '#16A085', '#2980B9', '#229954', '#E67E22', '#9B59B6',
        '#CB4335', '#17A2B8', '#28A745', '#FFC107', '#6F42C1', '#DC3545'
    ]

    for word_obj in all_words:
        if word_obj['clean'] in used_words or not word_obj['phones']:
            continue

        # Find exact rhymes first
        rhyming_words = pronouncing.rhymes(word_obj['clean'])

        # Find which of our words are in the rhyming list
        group_words = [word_obj]  # Start with current word

        for other_word_obj in all_words:
            if (other_word_obj['clean'] != word_obj['clean'] and
                other_word_obj['clean'] not in used_words and
                other_word_obj['phones']):

                # Check exact rhymes first
                if other_word_obj['clean'] in rhyming_words:
                    group_words.append(other_word_obj)
                # Check phonetic similarity for slant rhymes
                elif phonetic_similarity(word_obj['phones'], other_word_obj['phones']) >= 0.7:
                    group_words.append(other_word_obj)

        # Only create group if we have at least 2 words
        if len(group_words) >= 2:
            # Get rhyming part for syllable highlighting
            rhyme_part = pronouncing.rhyming_part(word_obj['phones'])

            rhyme_groups.append({
                'letter': chr(ord('A') + group_counter),
                'color': colors[group_counter % len(colors)],
                'words': group_words,
                'syllable_info': {
                    'rhyme_sound': rhyme_part,
                    'pattern': 'end_rhyme'
                }
            })

            # Mark all words in this group as used
            for gw in group_words:
                used_words.add(gw['clean'])

            group_counter += 1

    # Step 3: Create syllable highlights for multisyllabic words
    syllable_highlights = create_syllable_highlights(rhyme_groups)

    # Step 4: Format response for frontend
    rhyme_groups_dict = {}
    for group in rhyme_groups:
        rhyme_groups_dict[group['letter']] = group

    return {
        'lines': lines,
        'groups': rhyme_groups,
        'rhyme_groups': rhyme_groups_dict,
        'syllable_highlights': syllable_highlights
    }

def create_syllable_highlights(rhyme_groups):
    """Create syllable-level highlighting for multisyllabic words"""
    syllable_highlights = {}

    for group in rhyme_groups:
        group_color = group['color']
        rhyme_part = group['syllable_info']['rhyme_sound']

        for word_obj in group['words']:
            word_key = f"{word_obj['line_index']}_{word_obj['word_index']}"
            clean_word = word_obj['clean']
            original_word = word_obj['original']

            # Create syllable breakdown for highlighting
            syllables = create_syllable_breakdown(original_word, clean_word, rhyme_part, group_color)

            syllable_highlights[word_key] = {
                'word': original_word,
                'clean': clean_word,
                'syllables': syllables
            }

    return syllable_highlights

def create_syllable_breakdown(original_word, clean_word, rhyme_part, color):
    """Break word into syllables and identify rhyming parts"""
    syllables = []
    word_lower = clean_word.lower()

    # Simple words that should be highlighted completely
    simple_words = ['beat', 'meat', 'heat', 'sweet', 'neat', 'script', 'dipped', 'lipped']

    if word_lower in simple_words or len(word_lower) <= 4:
        # Highlight the whole word for simple/short words
        syllables.append({
            'text': original_word,
            'rhyme_group': rhyme_part,
            'color': color,
            'is_rhyming': True
        })
        return syllables

    # For multisyllabic words, try to identify the rhyming ending
    # More specific rhyming endings with better boundaries
    rhyming_patterns = [
        ('ipping', 'ipping'),  # tripping, dripping, stripping
        ('imping', 'imping'),  # pimping
        ('inder', 'inder'),    # grinder, finder
        ('iner', 'iner'),      # miner, diner
        ('igner', 'igner'),    # signer
        ('inor', 'inor'),      # minor
        ('uble', 'uble'),      # trouble, double, bubble
        ('ubtle', 'ubtle'),    # subtle
        ('ner', 'ner'),        # miner, signer (fallback)
        ('ing', 'ing'),        # general -ing words
        ('er', 'er'),          # general -er words
        ('ent', 'ent'),        # president, evident, etc.
        ('ant', 'ant'),        # hesitant, etc.
        ('tion', 'tion'),      # action, etc.
        ('sion', 'sion'),      # vision, etc.
        ('ly', 'ly'),          # quickly, etc.
        ('ty', 'ty'),          # beauty, etc.
        ('cy', 'cy'),          # policy, etc.
        ('est', 'est'),        # biggest, etc.
        ('ness', 'ness'),      # kindness, etc.
        ('ed', 'ed'),          # played, etc.
    ]

    rhyming_syllable = None
    prefix = original_word

    # Check for specific patterns first (most specific to least specific)
    for pattern, ending in rhyming_patterns:
        if word_lower.endswith(pattern):
            rhyming_syllable = original_word[-len(ending):]
            prefix = original_word[:-len(ending)]
            break

    # If no pattern found, use smart splitting for longer words
    if not rhyming_syllable and len(word_lower) >= 4:
        # For words like "grinder", "finder" - take last 2-3 chars as rhyming part
        if word_lower.endswith('er'):
            split_point = len(original_word) - 2
        elif word_lower.endswith('ing'):
            split_point = len(original_word) - 3
        else:
            split_point = max(1, len(original_word) - 3)

        prefix = original_word[:split_point]
        rhyming_syllable = original_word[split_point:]

    # Create syllable breakdown
    if prefix and rhyming_syllable and len(prefix) > 0:
        syllables.append({
            'text': prefix,
            'rhyme_group': None,
            'color': None,
            'is_rhyming': False
        })
        syllables.append({
            'text': rhyming_syllable,
            'rhyme_group': rhyme_part,
            'color': color,
            'is_rhyming': True
        })
    else:
        # Fallback: highlight whole word
        syllables.append({
            'text': original_word,
            'rhyme_group': rhyme_part,
            'color': color,
            'is_rhyming': True
        })

    return syllables

if __name__ == '__main__':
    print("Starting Rhyme Scheme Analyzer server...")
    print("Open http://localhost:8080 in your browser")
    print("Or try http://127.0.0.1:8080 if localhost is blocked")
    app.run(host='0.0.0.0', port=8080, debug=True)