from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import re
import pronouncing
import requests
from urllib.parse import quote
import lyricsgenius
import os
from pathlib import Path
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app)

# Initialize Genius API
def load_genius_token():
    """Load Genius API token from environment or .env file"""
    # Try environment variable first
    token = os.getenv('GENIUS_ACCESS_TOKEN')
    if token:
        return token

    # Try to load from .env file
    env_file = Path('.env')
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                if line.startswith('GENIUS_ACCESS_TOKEN='):
                    return line.split('=', 1)[1].strip()

    return None

# Initialize Genius client
genius_token = load_genius_token()
genius = None
if genius_token:
    try:
        genius = lyricsgenius.Genius(genius_token)
        genius.verbose = False  # Turn off status messages
        genius.remove_section_headers = True  # Remove [Verse 1], [Chorus], etc.
        genius.skip_non_songs = False  # Include all results
        genius.excluded_terms = []  # Don't exclude any terms
        print("✓ Genius API initialized successfully")
        print(f"✓ Token: {genius_token[:10]}...{genius_token[-10:]}")  # Show partial token for debugging
    except Exception as e:
        print(f"⚠ Warning: Failed to initialize Genius API: {e}")
        genius = None
else:
    print("⚠ Warning: No Genius API token found. Create a .env file with GENIUS_ACCESS_TOKEN.")
    genius = None

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/test-genius', methods=['GET'])
def test_genius():
    """Test endpoint to verify Genius API connectivity"""
    if not genius:
        return jsonify({'status': 'error', 'message': 'Genius API not initialized'})

    try:
        # Try a simple search that should work
        results = genius.search("test")
        return jsonify({
            'status': 'success',
            'message': 'Genius API is working',
            'results_count': len(results['hits']) if results and 'hits' in results else 0
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'API test failed: {str(e)}'})

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

@app.route('/search-lyrics', methods=['POST'])
def search_lyrics():
    try:
        data = request.get_json()
        artist = data.get('artist', '').strip()
        song = data.get('song', '').strip()

        if not artist or not song:
            return jsonify({'error': 'Artist and song name are required'}), 400

        # Check if Genius API is available
        if not genius:
            return jsonify({
                'success': False,
                'error': 'Genius API not configured. Please set up GENIUS_ACCESS_TOKEN in .env file.'
            }), 503

        try:
            # Search for the song using direct Genius API calls
            print(f"Searching for: {artist} - {song}")

            # Search for the song
            search_query = f"{song} {artist}"
            search_url = f"https://api.genius.com/search?q={quote(search_query)}"

            headers = {
                'Authorization': f'Bearer {genius_token}',
                'User-Agent': 'RhymeScheme'
            }

            # Search for the song
            search_response = requests.get(search_url, headers=headers, timeout=10)
            search_response.raise_for_status()

            search_data = search_response.json()
            hits = search_data.get('response', {}).get('hits', [])

            if not hits:
                return jsonify({
                    'success': False,
                    'error': f'No songs found for "{song}" by {artist}. Try different search terms.'
                }), 404

            # Find the best match
            best_match = None
            for hit in hits:
                result = hit.get('result', {})
                song_title = result.get('title', '').lower()
                artist_name = result.get('primary_artist', {}).get('name', '').lower()

                # Simple matching logic
                if (song.lower() in song_title or song_title in song.lower()) and \
                   (artist.lower() in artist_name or artist_name in artist.lower()):
                    best_match = result
                    break

            # If no exact match, use the first result
            if not best_match and hits:
                best_match = hits[0].get('result', {})

            if best_match:
                song_id = best_match.get('id')
                song_title = best_match.get('title')
                artist_name = best_match.get('primary_artist', {}).get('name')
                song_url = best_match.get('url')

                # Get lyrics by scraping the song page
                lyrics = scrape_genius_lyrics(song_url)

                if lyrics:
                    song_info = {
                        'success': True,
                        'lyrics': lyrics,
                        'artist': artist_name,
                        'song': song_title,
                        'url': song_url,
                        'genius_id': song_id
                    }

                    print(f"✓ Found lyrics for: {artist_name} - {song_title}")
                    return jsonify(song_info)
                else:
                    return jsonify({
                        'success': False,
                        'error': f'Found song but could not retrieve lyrics for "{song_title}" by {artist_name}'
                    }), 404
            else:
                return jsonify({
                    'success': False,
                    'error': f'No matching songs found for "{song}" by {artist}'
                }), 404

        except Exception as e:
            print(f"Genius API error: {str(e)}")
            return jsonify({
                'success': False,
                'error': f'Failed to fetch lyrics: {str(e)}'
            }), 503

    except Exception as e:
        print(f"Search error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Search failed: {str(e)}'
        }), 500

def scrape_genius_lyrics(song_url):
    """Scrape lyrics from Genius song page"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(song_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find lyrics container (Genius uses different class names that change)
        lyrics_divs = soup.find_all('div', {'data-lyrics-container': 'true'})

        if not lyrics_divs:
            # Try alternative selectors
            lyrics_divs = soup.find_all('div', class_=lambda x: x and 'lyrics' in x.lower())

        if not lyrics_divs:
            # Try more specific patterns
            lyrics_divs = soup.find_all('div', class_=lambda x: x and ('Lyrics__Container' in str(x)))

        if lyrics_divs:
            lyrics_text = ''
            for div in lyrics_divs:
                # Remove unwanted elements
                for unwanted in div.find_all(['script', 'style', 'div'], class_=lambda x: x and 'ad' in str(x).lower()):
                    unwanted.decompose()

                text = div.get_text(separator='\n', strip=True)
                lyrics_text += text + '\n'

            # Clean up the lyrics
            lyrics_text = lyrics_text.strip()

            # Remove common artifacts
            lines = lyrics_text.split('\n')
            cleaned_lines = []

            for line in lines:
                line = line.strip()
                # Skip empty lines and common artifacts
                if line and not line.startswith('[') and not line.endswith(']'):
                    # Remove section headers like [Verse 1], [Chorus], etc.
                    if not (line.startswith('[') and line.endswith(']')):
                        cleaned_lines.append(line)

            if cleaned_lines:
                return '\n'.join(cleaned_lines)

        return None

    except Exception as e:
        print(f"Error scraping lyrics: {e}")
        return None

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