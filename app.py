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

def find_all_rhymes(text):
    """Main rhyme detection function using pronouncing library"""
    lines = text.split('\n')
    all_words = []

    # Step 1: Extract all words with positions
    for line_idx, line in enumerate(lines):
        words = line.split()
        for word_idx, word in enumerate(words):
            clean = clean_word(word)
            if len(clean) >= 2:
                all_words.append({
                    'original': word,
                    'clean': clean,
                    'line_index': line_idx,
                    'word_index': word_idx
                })

    # Step 2: Find rhyme groups using pronouncing library
    rhyme_groups = []
    used_words = set()
    group_counter = 0
    colors = [
        '#C0392B', '#138D75', '#1F618D', '#27AE60', '#F39C12', '#8E44AD',
        '#E74C3C', '#16A085', '#2980B9', '#229954', '#E67E22', '#9B59B6',
        '#CB4335', '#17A2B8', '#28A745', '#FFC107', '#6F42C1', '#DC3545'
    ]

    for word_obj in all_words:
        if word_obj['clean'] in used_words:
            continue

        # Find all words that rhyme with this one
        rhyming_words = pronouncing.rhymes(word_obj['clean'])

        # Find which of our words are in the rhyming list
        group_words = [word_obj]  # Start with current word
        for other_word_obj in all_words:
            if (other_word_obj['clean'] != word_obj['clean'] and
                other_word_obj['clean'] not in used_words and
                other_word_obj['clean'] in rhyming_words):
                group_words.append(other_word_obj)

        # Only create group if we have at least 2 words
        if len(group_words) >= 2:
            # Get rhyming part for syllable highlighting
            phones = pronouncing.phones_for_word(word_obj['clean'])
            rhyme_part = pronouncing.rhyming_part(phones[0]) if phones else None

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

    # For multisyllabic words, try to identify the rhyming ending
    if len(word_lower) > 3:
        # More specific rhyming endings with better boundaries
        rhyming_patterns = [
            ('ipping', 'ipping'),  # tripping, dripping, stripping
            ('iner', 'iner'),      # miner, diner, signer
            ('igner', 'igner'),    # signer
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
    else:
        # Short word - highlight the whole thing
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