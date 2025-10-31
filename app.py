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
        sensitivity = data.get('sensitivity', 70)  # Default to 70%

        if not text:
            return jsonify({'error': 'No text provided'}), 400

        # Convert percentage to threshold with better mapping
        # 0% = 0.95 (near perfect only), 50% = 0.7 (balanced), 100% = 0.4 (loose)
        if sensitivity <= 50:
            # 0-50%: 0.95 to 0.7 (strict to balanced)
            threshold = 0.95 - (sensitivity / 50.0 * 0.25)
        else:
            # 50-100%: 0.7 to 0.4 (balanced to loose)
            threshold = 0.7 - ((sensitivity - 50) / 50.0 * 0.3)

        analysis = find_all_rhymes(text, threshold)
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
    """Enhanced phonetic similarity with better rhyme accuracy"""
    if not phones1 or not phones2:
        return 0.0

    # Get rhyming parts (suffix similarity is most important for rhymes)
    rhyme1 = pronouncing.rhyming_part(phones1)
    rhyme2 = pronouncing.rhyming_part(phones2)

    if not rhyme1 or not rhyme2:
        return 0.0

    # For exact matches
    if rhyme1 == rhyme2:
        return 1.0

    # Split into phonemes
    phonemes1 = rhyme1.split()
    phonemes2 = rhyme2.split()

    if len(phonemes1) == 0 or len(phonemes2) == 0:
        return 0.0

    # Enhanced similarity calculation
    return calculate_enhanced_phonetic_similarity(phonemes1, phonemes2)

def calculate_enhanced_phonetic_similarity(phonemes1, phonemes2):
    """More sophisticated phonetic similarity calculation"""

    # Vowel phonemes (including stressed and unstressed variants)
    vowels = {'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW'}

    # Extract vowel sounds and their positions
    vowels1 = [(i, p) for i, p in enumerate(phonemes1) if any(p.startswith(v) for v in vowels)]
    vowels2 = [(i, p) for i, p in enumerate(phonemes2) if any(p.startswith(v) for v in vowels)]

    # If no vowels, can't be a good rhyme
    if not vowels1 or not vowels2:
        return 0.0

    # Score components
    vowel_score = 0.0
    consonant_score = 0.0
    ending_score = 0.0

    # 1. Vowel sound similarity (most important for rhymes)
    last_vowel1 = vowels1[-1][1]  # Last vowel sound
    last_vowel2 = vowels2[-1][1]

    # Remove stress numbers for comparison
    clean_vowel1 = ''.join(c for c in last_vowel1 if c.isalpha())
    clean_vowel2 = ''.join(c for c in last_vowel2 if c.isalpha())

    if clean_vowel1 == clean_vowel2:
        vowel_score = 1.0
    elif are_similar_vowels(clean_vowel1, clean_vowel2):
        vowel_score = 0.7
    else:
        # If main vowel sounds don't match, it's not a good rhyme
        return 0.0

    # 2. Ending consonant similarity
    min_len = min(len(phonemes1), len(phonemes2))
    max_len = max(len(phonemes1), len(phonemes2))

    # Check how many phonemes match from the end
    matching_from_end = 0
    for i in range(min_len):
        if phonemes1[-(i+1)] == phonemes2[-(i+1)]:
            matching_from_end += 1
        else:
            break

    if matching_from_end >= 2:  # At least 2 phonemes match
        ending_score = matching_from_end / max_len
    elif matching_from_end == 1 and min_len <= 2:  # Short words with 1 match
        ending_score = 0.5

    # 3. Consonant cluster similarity (for words ending in similar sounds)
    consonant_score = calculate_consonant_similarity(phonemes1, phonemes2)

    # 4. Apply penalties for length mismatches
    length_penalty = 1.0
    if max_len > min_len * 2:  # Very different lengths
        length_penalty = 0.5

    # Final weighted score
    final_score = (vowel_score * 0.5 + ending_score * 0.3 + consonant_score * 0.2) * length_penalty

    return min(final_score, 1.0)

def are_similar_vowels(vowel1, vowel2):
    """Check if two vowel sounds are similar enough for slant rhymes"""
    similar_groups = [
        {'IH', 'IY'},  # bit/beat
        {'EH', 'AE'},  # bet/bat
        {'AH', 'UH'},  # but/put
        {'OW', 'AO'},  # boat/bought
        {'AY', 'EY'},  # bite/bait
        {'AW', 'OW'},  # bout/boat
    ]

    for group in similar_groups:
        if vowel1 in group and vowel2 in group:
            return True
    return False

def calculate_consonant_similarity(phonemes1, phonemes2):
    """Calculate similarity of consonant patterns"""
    # Focus on ending consonants after the main vowel
    vowels = {'AE', 'AH', 'AO', 'AW', 'AY', 'EH', 'ER', 'EY', 'IH', 'IY', 'OW', 'OY', 'UH', 'UW'}

    # Find last vowel position in each word
    last_vowel_pos1 = -1
    last_vowel_pos2 = -1

    for i, p in enumerate(phonemes1):
        if any(p.startswith(v) for v in vowels):
            last_vowel_pos1 = i

    for i, p in enumerate(phonemes2):
        if any(p.startswith(v) for v in vowels):
            last_vowel_pos2 = i

    if last_vowel_pos1 == -1 or last_vowel_pos2 == -1:
        return 0.0

    # Get consonants after last vowel
    consonants1 = phonemes1[last_vowel_pos1 + 1:]
    consonants2 = phonemes2[last_vowel_pos2 + 1:]

    if not consonants1 and not consonants2:
        return 1.0  # Both end in vowels

    if len(consonants1) == 0 or len(consonants2) == 0:
        return 0.3  # One ends in vowel, one in consonant

    # Count matching consonants
    matches = sum(1 for c1, c2 in zip(consonants1, consonants2) if c1 == c2)
    max_consonants = max(len(consonants1), len(consonants2))

    return matches / max_consonants if max_consonants > 0 else 0.0

def calculate_rhyme_score(text, rhyme_groups, threshold):
    """Calculate comprehensive rhyme quality score"""
    lines = text.split('\n')
    total_lines = len([line for line in lines if line.strip()])
    all_words = text.split()
    total_words = len(all_words)

    if total_words == 0:
        return {
            'overall_score': 0,
            'base_density': 0,
            'syllable_complexity': 0,
            'rhyme_quality': 0,
            'vocabulary_diversity': 0,
            'pattern_sophistication': 0,
            'statistics': {}
        }

    # Count rhyming words and analyze quality
    total_rhyming_words = 0
    perfect_rhymes = 0
    slant_rhymes = 0
    syllable_points = 0

    for group in rhyme_groups:
        group_size = len(group['words'])
        total_rhyming_words += group_size

        # Analyze syllable complexity
        for word_obj in group['words']:
            word = word_obj['clean']
            syllable_count = estimate_syllables(word)
            syllable_points += max(1, syllable_count)

            # Determine if perfect or slant rhyme
            if group_size > 1:
                # Check against first word in group for quality assessment
                first_word = group['words'][0]
                if word != first_word['clean']:
                    exact_rhymes = pronouncing.rhymes(first_word['clean'])
                    if word in exact_rhymes:
                        perfect_rhymes += 1
                    else:
                        slant_rhymes += 1

    # Calculate unique words
    unique_words = len(set(word.lower() for word in all_words))

    # 1. Base Rhyme Density
    base_density = (total_rhyming_words / total_words) * 100 if total_words > 0 else 0

    # 2. Syllable Complexity Multiplier
    avg_syllable_bonus = (syllable_points - total_rhyming_words) * 0.2 / max(total_rhyming_words, 1)
    syllable_multiplier = 1 + avg_syllable_bonus

    # 3. Rhyme Quality Factor
    total_rhyme_pairs = perfect_rhymes + slant_rhymes
    if total_rhyme_pairs > 0:
        quality_factor = (perfect_rhymes * 1.0 + slant_rhymes * 0.7) / total_rhyme_pairs
    else:
        quality_factor = 1.0

    # 4. Vocabulary Diversity Bonus
    diversity_bonus = 1 + (unique_words / total_words * 0.3)

    # 5. Pattern Sophistication
    num_groups = len(rhyme_groups)
    avg_group_size = total_rhyming_words / max(num_groups, 1)
    pattern_score = (num_groups * avg_group_size) / max(total_lines, 1) * 10

    # Final calculation
    core_score = base_density * syllable_multiplier * quality_factor * diversity_bonus
    final_score = min(100, core_score + pattern_score)

    # Detailed statistics
    statistics = {
        'total_words': total_words,
        'total_lines': total_lines,
        'rhyming_words': total_rhyming_words,
        'unique_words': unique_words,
        'rhyme_groups': num_groups,
        'perfect_rhymes': perfect_rhymes,
        'slant_rhymes': slant_rhymes,
        'avg_syllables': syllable_points / max(total_rhyming_words, 1),
        'rhyme_density_percent': round(base_density, 1),
        'vocabulary_diversity_percent': round((unique_words / total_words) * 100, 1)
    }

    return {
        'overall_score': round(final_score, 1),
        'base_density': round(base_density, 1),
        'syllable_complexity': round(syllable_multiplier, 2),
        'rhyme_quality': round(quality_factor, 2),
        'vocabulary_diversity': round(diversity_bonus, 2),
        'pattern_sophistication': round(pattern_score, 1),
        'statistics': statistics
    }

def estimate_syllables(word):
    """Estimate syllable count for a word"""
    word = word.lower()
    if not word:
        return 0

    # Simple syllable estimation
    vowels = "aeiouy"
    syllable_count = 0
    prev_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not prev_was_vowel:
            syllable_count += 1
        prev_was_vowel = is_vowel

    # Handle silent e
    if word.endswith('e') and syllable_count > 1:
        syllable_count -= 1

    return max(1, syllable_count)

def get_optimal_color(used_colors, available_colors):
    """Select color with maximum contrast from recently used colors"""
    if not used_colors:
        return available_colors[0]

    if len(used_colors) < len(available_colors):
        # For first few colors, use predefined high-contrast sequence
        contrast_sequence = [0, 9, 4, 13, 2, 11, 6, 15, 1, 10, 3, 12, 5, 14, 7, 16, 8, 17]
        for idx in contrast_sequence:
            if idx < len(available_colors) and available_colors[idx] not in used_colors:
                return available_colors[idx]

    # Fallback to cycling if we've used all unique colors
    return available_colors[len(used_colors) % len(available_colors)]

def find_all_rhymes(text, threshold=0.7):
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

    # High-contrast color palette with maximum visual separation
    base_colors = [
        '#C0392B',  # Deep Red
        '#138D75',  # Teal
        '#F39C12',  # Orange
        '#8E44AD',  # Purple
        '#27AE60',  # Green
        '#1F618D',  # Blue
        '#E67E22',  # Dark Orange
        '#9B59B6',  # Light Purple
        '#229954',  # Dark Green
        '#2980B9',  # Light Blue
        '#DC3545',  # Bright Red
        '#17A2B8',  # Cyan
        '#28A745',  # Bright Green
        '#FFC107',  # Yellow
        '#6F42C1',  # Indigo
        '#CB4335',  # Burgundy
        '#16A085',  # Dark Teal
        '#E74C3C'   # Crimson
    ]

    used_colors = []

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
                elif phonetic_similarity(word_obj['phones'], other_word_obj['phones']) >= threshold:
                    group_words.append(other_word_obj)

        # Only create group if we have at least 2 words
        if len(group_words) >= 2:
            # Get rhyming part for syllable highlighting
            rhyme_part = pronouncing.rhyming_part(word_obj['phones'])

            # Select optimal color with maximum contrast
            optimal_color = get_optimal_color(used_colors, base_colors)
            used_colors.append(optimal_color)

            rhyme_groups.append({
                'letter': chr(ord('A') + group_counter),
                'color': optimal_color,
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

    # Step 4: Calculate comprehensive scoring
    score_data = calculate_rhyme_score(text, rhyme_groups, threshold)

    # Step 5: Format response for frontend
    rhyme_groups_dict = {}
    for group in rhyme_groups:
        rhyme_groups_dict[group['letter']] = group

    return {
        'lines': lines,
        'groups': rhyme_groups,
        'rhyme_groups': rhyme_groups_dict,
        'syllable_highlights': syllable_highlights,
        'score': score_data
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