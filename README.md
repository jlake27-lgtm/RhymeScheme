# RhymeScheme Analyzer

A sophisticated web-based rhyme scheme analyzer with real-time audio synchronization that identifies and highlights rhyming patterns in poetry, rap lyrics, and other text.

## 🚀 Quick Start (30 Seconds)

```bash
# 1. Clone the repository
git clone https://github.com/jlake27-lgtm/RhymeScheme.git
cd RhymeScheme

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On macOS/Linux
# venv\Scripts\activate     # On Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start the server
python app.py

# 5. Open browser to http://localhost:8080
```

**Test with sample text:**
```
Tripping off the beat kinda, dripping off the meat grinder
Heat miner, pimping, stripping, soft sweet minor
```

## 📋 Requirements

- **Python 3.7+** (Download from [python.org](https://www.python.org/downloads/))
- **pip** (included with Python)
- **Internet connection** (for API features)

## ⚡ Core Features

### 🎯 Rhyme Analysis
- **Accurate Detection**: CMU Pronunciation Dictionary for phonetic analysis
- **Multisyllabic Highlighting**: Only highlights rhyming parts (`grind**er**`, `find**er**`)
- **Adjustable Sensitivity**: 0-100% slider for precision control
- **Smart Color Coding**: Maximum contrast colors for visual clarity

### 🎬 Real-Time Audio Sync (v2.1.0)
- **YouTube Integration**: Automatic audio playback with lyrics
- **Karaoke-Style Timing**: Millisecond-precise synchronization
- **Fullscreen Mode**: Immersive presentation view
- **Song Search**: Dynamic video search via YouTube Data API v3

### 📊 Scientific Scoring
- **0-100 Point System** based on:
  - Rhyme density and distribution (30 pts)
  - Syllable complexity analysis (25 pts)
  - Phonetic quality assessment (20 pts)
  - Vocabulary diversity metrics (15 pts)
  - Pattern sophistication scoring (10 pts)

## 🔧 API Configuration (Optional but Recommended)

### YouTube Data API v3 Setup
1. Visit [Google Cloud Console](https://console.developers.google.com/)
2. Create new project or select existing
3. Enable "YouTube Data API v3"
4. Create API key (restrict to YouTube Data API v3)

### Genius API Setup
1. Visit [Genius API](https://genius.com/api-clients)
2. Create new API client
3. Copy access token

### Environment Configuration
```bash
# Copy template
cp .env.example .env

# Edit .env file
GENIUS_ACCESS_TOKEN=your_genius_token_here
YOUTUBE_API_KEY=your_youtube_api_key_here
```

**Without APIs:** App works with ~25 popular songs in fallback database

## 🎮 Usage Guide

### Basic Rhyme Analysis
1. **Enter Text**: Paste lyrics, poetry, or text into the input area
2. **Analyze**: Click "Analyze Rhyme Scheme"
3. **Adjust Sensitivity**: Use slider to fine-tune detection
4. **View Results**:
   - **Highlighted text** with rhyming syllables marked
   - **Rhyme groups** with color coding
   - **Statistics** with comprehensive metrics
   - **Score breakdown** showing quality factors

### Audio Synchronization
1. **Search Song**: Enter artist and song name
2. **Load Audio**: System finds YouTube video and timing data
3. **Start Sync**: Click sync button for real-time highlighting
4. **Fullscreen Mode**: Press button for immersive experience

### Expected Results
**Input:**
```
Tripping off the beat kinda, dripping off the meat grinder
Heat miner, pimping, stripping, soft sweet minor
```

**Output:**
- **Group A (Red)**: `tripp**ing**, dripp**ing**, stripp**ing**`
- **Group B (Blue)**: `**beat**, **meat**, **heat**, **sweet**`
- **Group C (Green)**: `mi**ner**, mi**nor**`
- **Score**: 78/100 (Excellent)

## 📁 Project Structure

```
RhymeScheme/
├── app.py              # Main Flask backend (1,000+ lines)
├── index.html          # Frontend interface (2,000+ lines)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment template
├── CLAUDE.md          # Development guidelines
├── README.md          # This documentation
└── venv/              # Virtual environment
```

## 🔗 API Reference

### POST `/analyze`
Analyzes text for rhyme patterns and scoring.

**Request:**
```json
{
  "text": "Your lyrics here",
  "sensitivity": 70
}
```

**Response:**
```json
{
  "groups": [...],
  "syllable_highlights": {...},
  "score": {
    "overall": 78,
    "breakdown": {...}
  },
  "statistics": {...}
}
```

### POST `/search-audio`
Searches for YouTube audio using song/artist.

**Request:**
```json
{
  "artist": "Artist Name",
  "song": "Song Title"
}
```

### POST `/search-timed-lyrics`
Retrieves LRC timing data for synchronization.

## 🚨 Troubleshooting

### Common Issues

**"Failed to analyze text"**
```bash
# Check if server is running
python app.py
# Should show: "Running on http://127.0.0.1:8080"
```

**No highlighting appears**
- Check browser console for JavaScript errors
- Ensure using supported browser (Chrome, Firefox, Safari, Edge)

**Port 8080 already in use**
```bash
# Kill existing process
lsof -ti:8080 | xargs kill -9

# Or change port in app.py
app.run(port=8081)
```

**API quota exceeded**
- YouTube API: 100 free searches/day
- Genius API: 1000 requests/day
- App falls back to hardcoded database automatically

### Performance Tips
- **Large texts**: Use sensitivity slider to optimize processing
- **Mobile**: App is fully responsive on all screen sizes
- **Memory**: Typical usage <50MB RAM

## 🔮 Version History

### v2.1.0 (Current - Active Development)
- ✅ **Real-Time Audio Sync**: YouTube + LRC timing integration
- ✅ **YouTube Data API v3**: Dynamic video search
- ✅ **Fullscreen Sync Mode**: Immersive karaoke-style presentation
- ✅ **Enhanced Fallback**: Intelligent degradation system
- 🚧 **Performance Optimization**: Sub-50ms timing accuracy

### v2.0.0 (Released)
- ✅ **Enhanced Phonetic Analysis**: Advanced vowel-focused detection
- ✅ **Sensitivity Control**: 0-100% adjustable precision
- ✅ **Scientific Scoring**: Multi-factor 0-100 point system
- ✅ **Advanced Statistics**: 10+ comprehensive metrics
- ✅ **Smart Color Selection**: Maximum contrast sequences
- ✅ **Collapsible UI**: Organized expandable sections

### v1.0.0 (Initial Release)
- ✅ Accurate CMU dictionary-based rhyme detection
- ✅ Multisyllabic highlighting with syllable boundaries
- ✅ Clean responsive web interface
- ✅ Dark/light theme support

## 🛠 Development

### Dependencies
- **Flask 2.3.3**: Web framework
- **pronouncing 0.2.0**: CMU Pronunciation Dictionary
- **syncedlyrics 1.0.1**: LRC timing data access
- **lyricsgenius 3.0.1**: Lyrics fetching
- **requests 2.31.0**: HTTP client
- **python-dotenv 1.0.0**: Environment variables

### Testing
```bash
# Test rhyme detection
python test_rhymes.py

# Test API endpoints
curl -X POST http://localhost:8080/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "cat hat bat sat"}'

# Test audio search
curl -X POST http://localhost:8080/search-audio \
  -H "Content-Type: application/json" \
  -d '{"artist": "Artist", "song": "Song"}'
```

### Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **CMU Pronunciation Dictionary**: Accurate phonetic data
- **Allison Parrish**: Creator of `pronouncing` library
- **Flask Team**: Excellent web framework
- **YouTube Data API**: Audio content access
- **Genius**: Lyrics database

---

**Made with ❤️ for poets, rappers, and word enthusiasts.**

🎯 **Ready to explore?** Start with the [Quick Start](#-quick-start-30-seconds) above!