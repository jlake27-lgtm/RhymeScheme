# Claude Configuration for RhymeScheme Project

## 🚀 Project Overview

RhymeScheme is a sophisticated web-based rhyme analyzer with real-time audio synchronization. The project combines advanced phonetic analysis with YouTube integration for karaoke-style lyric presentation.

**Current Version**: v2.1.0 (Active Development)
**Architecture**: Flask backend + Vanilla JavaScript frontend
**Primary Goals**: Accurate rhyme detection + Real-time audio sync

## 📋 Essential Commands

### Development Server
```bash
python app.py                           # Start Flask dev server (port 8080)
source venv/bin/activate                 # Activate venv (macOS/Linux)
venv\Scripts\activate                    # Activate venv (Windows)
pip install -r requirements.txt         # Install dependencies
lsof -ti:8080 | xargs kill -9           # Kill processes on port 8080
```

### Testing & Quality
```bash
python test_rhymes.py                   # Test rhyme detection
curl -X POST http://localhost:8080/analyze -H "Content-Type: application/json" -d '{"text":"test"}' # Test API
python -m py_compile app.py             # Syntax check
```

### Git Workflow
```bash
git add . && git commit -m "message"    # Standard commit
git push origin main                    # Push to remote
git status && git diff                  # Check changes
```

## 🏗 Architecture & File Structure

### Core Files
- **`app.py`** (1,000+ lines): Complete Flask backend with all logic
- **`index.html`** (2,000+ lines): Frontend with embedded CSS/JS
- **`requirements.txt`**: 9 Python dependencies
- **`.env.example`**: Environment variable template
- **`.env`**: Actual API keys (never commit)

### Key Dependencies
```python
Flask==2.3.3              # Web framework
pronouncing==0.2.0         # CMU dictionary rhyme detection
syncedlyrics==1.0.1        # LRC timing data for sync
lyricsgenius==3.0.1        # Genius API lyrics fetching
requests==2.31.0           # HTTP client for APIs
python-dotenv==1.0.0       # Environment variable management
Flask-CORS==4.0.0          # Cross-origin requests
nltk==3.8.1               # Natural language processing
reportlab==4.0.4          # PDF generation (future feature)
```

## 🔧 Development Guidelines

### Backend (Python/Flask)
- **Single-file architecture**: Keep all logic in `app.py` for simplicity
- **Flask + CORS**: Enable cross-origin requests for frontend
- **Error handling**: Comprehensive try/catch blocks with meaningful messages
- **API design**: Consistent JSON responses with success/error states
- **Environment variables**: Use `.env` for API keys, never hardcode

### Frontend (HTML/CSS/JS)
- **Vanilla JavaScript**: No frameworks for simplicity and performance
- **Responsive design**: CSS Grid/Flexbox for mobile compatibility
- **Theme management**: CSS custom properties for dark/light modes
- **localStorage**: Persist user preferences (theme, settings)
- **Accessibility**: Semantic HTML, ARIA labels, keyboard navigation

### API Integration Patterns

#### YouTube Data API v3
```python
# app.py integration pattern
youtube_api_key = load_youtube_api_key()
def search_audio():
    if not youtube_api_key:
        return fallback_youtube_search()
    # Real API call with fallback
```

#### Genius API
```python
# app.py integration pattern
genius = lyricsgenius.Genius(genius_access_token)
def search_lyrics():
    # Handle rate limits and errors gracefully
```

#### LRC Timing Integration
```python
# app.py integration pattern
import syncedlyrics
def search_timed_lyrics():
    lrc_content = syncedlyrics.search(f"{song} {artist}")
    return parse_lrc_content(lrc_content)
```

## 🎯 Core Algorithm Implementation

### Rhyme Detection
```python
# Primary method: pronouncing library (CMU dictionary)
import pronouncing
rhymes = pronouncing.rhymes(word)

# Backup: phonetic similarity analysis
def phonetic_similarity(word1, word2, threshold=0.7):
    # Vowel-focused comparison with stress patterns
    pass
```

### Sensitivity Control
```python
# Dynamic threshold mapping (0-100% user input)
def map_sensitivity(sensitivity_percent):
    if sensitivity_percent <= 50:
        return 0.95 - (sensitivity_percent * 0.005)  # High threshold
    else:
        return 0.7 - ((sensitivity_percent - 50) * 0.006)  # Lower threshold
```

### Scoring System (0-100 points)
```python
def calculate_score(analysis_data):
    score_breakdown = {
        'density': min(30, density_score),           # 30 points max
        'syllable_complexity': min(25, syll_score), # 25 points max
        'quality': min(20, quality_score),          # 20 points max
        'diversity': min(15, diversity_score),      # 15 points max
        'sophistication': min(10, soph_score)       # 10 points max
    }
    return sum(score_breakdown.values())
```

### Color Management
```python
# Maximum contrast color sequences
def get_smart_colors(theme='dark'):
    if theme == 'dark':
        return ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']
    else:
        return ['#e74c3c', '#16a085', '#2980b9', '#27ae60', '#f39c12']
```

## 🎬 Audio Sync Implementation

### Frontend Pattern
```javascript
// Real-time sync with 50ms polling
function syncLyrics() {
    const currentTime = player.getCurrentTime() * 1000;
    for (let timing of timingData) {
        if (currentTime >= timing.timestamp) {
            highlightLine(timing.text);
        }
    }
    setTimeout(syncLyrics, 50);
}
```

### Backend Integration
```python
# Merge timing with rhyme analysis
def merge_timing_with_analysis(analysis_result, timing_data):
    # Intelligent line matching between LRC and analysis
    # Return synchronized data structure
```

## 🔑 Environment Configuration

### Required API Keys
```bash
# .env file structure
GENIUS_ACCESS_TOKEN=your_genius_token_here      # From genius.com/api-clients
YOUTUBE_API_KEY=your_youtube_api_key_here       # From console.developers.google.com
```

### API Quota Management
- **YouTube API**: 100 free searches/day → Intelligent fallback to hardcoded DB
- **Genius API**: 1000 requests/day → Graceful degradation
- **LRC Database**: Unlimited (via syncedlyrics)

## 🚨 Common Issues & Solutions

### Backend Issues
```python
# Issue: API quota exceeded
# Solution: Implement intelligent fallbacks
def fallback_youtube_search(artist, song, search_query):
    # Use expanded hardcoded database with strict matching

# Issue: LRC parsing fails
# Solution: Robust error handling
def parse_lrc_content(lrc_content):
    try:
        # Parse with multiple regex patterns
    except Exception as e:
        print(f"LRC parsing failed: {e}")
        return None
```

### Frontend Issues
```javascript
// Issue: API calls fail
// Solution: Comprehensive error handling
async function getYouTubeVideoId(artist, song) {
    try {
        const response = await fetch('/search-audio', {...});
        if (!response.ok) throw new Error('API failed');
        return await response.json();
    } catch (error) {
        console.error('Search failed:', error);
        return null;
    }
}
```

### Performance Optimization
- **Backend**: Cache color calculations, optimize regex patterns
- **Frontend**: Minimize DOM manipulation, use efficient highlighting
- **API**: Implement request throttling and caching
- **Memory**: Keep typical usage under 50MB

## 📊 Testing Strategy

### Unit Testing
```bash
# Test rhyme detection accuracy
python test_rhymes.py

# Test API endpoints
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "cat hat bat"}'
```

### Integration Testing
```bash
# Test full pipeline: search → timing → analysis → sync
# Test API fallbacks when quotas exceeded
# Test cross-browser compatibility
```

### Performance Testing
```bash
# Test with large texts (1000+ words)
# Test real-time sync precision (<50ms accuracy)
# Test mobile responsiveness
```

## 🎯 Development Workflow

### Feature Development
1. **Plan**: Use TodoWrite tool for task tracking
2. **Implement**: Follow architecture patterns above
3. **Test**: Comprehensive testing before commit
4. **Document**: Update README.md and CLAUDE.md as needed
5. **Deploy**: Commit with descriptive messages

### Code Quality Standards
- **Python**: Follow PEP 8, comprehensive error handling
- **JavaScript**: ES6+ features, consistent naming
- **CSS**: Custom properties, mobile-first design
- **Comments**: Only when business logic is complex
- **Security**: Never expose API keys, sanitize inputs

### Git Commit Patterns
```bash
# Feature commits
git commit -m "Implement YouTube Data API v3 integration for unlimited song search"

# Bug fixes
git commit -m "Fix frontend getYouTubeVideoId() to call backend API instead of hardcoded values"

# Documentation
git commit -m "Update documentation for v2.1.0 with real-time sync features"
```

## 🚀 Future Development Roadmap

### Immediate Goals (v2.1.0)
- ✅ YouTube Data API v3 integration
- ✅ Real-time audio synchronization
- ✅ LRC timing integration
- 🚧 Performance optimization (<50ms sync)

### Next Features (v2.2.0)
- 🚧 Export functionality (PDF, JSON, formatted text)
- 🚧 Pattern recognition for complex rhyme schemes
- 🚧 Multi-song batch analysis
- 🚧 Custom audio file upload support

### Long-term Vision (v3.0.0)
- AI-powered rhyme pattern analysis
- Collaborative editing features
- Advanced export options
- Mobile app development

## 🔧 Troubleshooting Guide

### Quick Diagnostics
```bash
# Server not starting
python app.py  # Should show "Running on http://127.0.0.1:8080"

# Port conflicts
lsof -ti:8080  # Check what's using port 8080
lsof -ti:8080 | xargs kill -9  # Kill conflicting processes

# Dependencies missing
pip install -r requirements.txt  # Reinstall all deps

# API issues
grep -r "API" .env  # Check if API keys are configured
```

### Performance Issues
- Large texts: Adjust sensitivity slider
- Slow sync: Check 50ms polling interval
- Memory leaks: Monitor browser dev tools
- API timeouts: Verify internet connection

Remember: This project prioritizes simplicity, accuracy, and real-time performance. Keep the architecture clean and maintainable while adding powerful features.