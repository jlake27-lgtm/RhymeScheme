# Claude Configuration for RhymeScheme Python Project

## Bash Commands
- python app.py: Start Flask development server (port 8080)
- pip install -r requirements.txt: Install Python dependencies
- source venv/bin/activate: Activate virtual environment (macOS/Linux)
- venv\Scripts\activate: Activate virtual environment (Windows)
- python -m venv venv: Create virtual environment
- lsof -ti:8080 | xargs kill -9: Kill process on port 8080

## Project Structure
- app.py: Main Flask application with all backend logic
- index.html: Frontend interface with JavaScript and CSS
- requirements.txt: Python dependencies
- .env: Environment variables (Genius API token)
- .env.example: Template for environment setup

## Code Style & Architecture

### Backend (Python/Flask)
- Use Flask with CORS support for cross-origin requests
- Keep all logic in app.py for simplicity (single-file architecture)
- Use snake_case for Python functions and variables
- Implement comprehensive error handling with try/catch blocks
- Return consistent JSON response format from API endpoints

### Frontend (JavaScript/HTML/CSS)
- Use vanilla JavaScript (no frameworks) for simplicity
- Implement responsive design with CSS Grid/Flexbox
- Use CSS custom properties (variables) for theme management
- Support both dark and light modes with localStorage persistence
- Use semantic HTML elements and ARIA labels for accessibility

### Key Implementation Guidelines

#### Rhyme Detection Algorithm
- Use `pronouncing` library as primary rhyme detection method
- Implement phonetic similarity as backup using CMU pronunciation dictionary
- Support adjustable sensitivity (0-100%) with dynamic threshold mapping:
  - 0-50%: High threshold (0.7-0.95) for strict rhyming
  - 51-100%: Lower threshold (0.4-0.7) for loose rhyming
- Focus on vowel sounds and stress patterns for accuracy

#### Color Management
- Use smart color selection with maximum contrast sequences
- Maintain separate color palettes for light and dark themes
- Ensure accessibility with sufficient color contrast ratios
- Avoid adjacent similar colors that could cause confusion

#### Scoring System
- Implement scientific 0-100 scoring with multi-factor analysis:
  - Rhyme Density (30 points): Distribution and coverage
  - Syllable Complexity (25 points): Average syllables and variation
  - Phonetic Quality (20 points): Strength of rhyme matches
  - Vocabulary Diversity (15 points): Unique word ratio
  - Pattern Sophistication (10 points): Rhyme scheme complexity
- Provide detailed breakdown with individual component scores

#### UI/UX Design Patterns
- Use collapsible sections for better information organization
- Implement real-time updates for sensitivity adjustments
- Display comprehensive statistics (10+ metrics) in organized format
- Support live re-analysis without page refresh
- Maintain responsive design across all screen sizes

## Testing & Validation
- Test rhyme detection accuracy with various text types (poetry, rap lyrics, prose)
- Validate scoring system with sample songs of known quality
- Ensure cross-browser compatibility (Chrome, Firefox, Safari, Edge)
- Test mobile responsiveness on different screen sizes
- Verify theme switching and localStorage persistence

## Development Workflow
- Always test locally with python app.py before committing
- Use meaningful commit messages with emoji prefixes where appropriate
- Test major features with sample texts before considering complete
- Maintain backward compatibility with existing API endpoints
- Document new features in README.md changelog section

## Environment Setup
- Create .env file from .env.example template
- Add Genius API token for lyrics search functionality
- Use virtual environment to isolate dependencies
- Keep sensitive information out of version control

## API Design Principles
- Accept optional sensitivity parameter in /analyze endpoint
- Return comprehensive response including score, statistics, and highlights
- Maintain consistent JSON structure across API versions
- Include error handling with meaningful error messages
- Support both text analysis and full lyric processing

## Performance Considerations
- Optimize phonetic analysis for real-time updates
- Cache color calculations to improve rendering speed
- Minimize DOM manipulation for better responsiveness
- Use efficient algorithms for syllable detection and highlighting
- Keep memory usage low for large text processing

## Future Feature Guidelines
- Plan audio synchronization with careful consideration of complexity
- Design export features with multiple format support
- Consider pattern recognition for advanced rhyme scheme analysis
- Implement batch processing capabilities for multiple songs
- Maintain simple, intuitive user interface despite feature growth