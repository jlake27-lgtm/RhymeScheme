# Claude Configuration for Node.js Project

## Bash Commands
- npm install: Install dependencies
- npm run dev: Start development server
- npm run build: Build the project
- npm test: Run tests
- npm run lint: Run linter

## Code Style
- Use ES modules (import/export) syntax, not CommonJS (require)
- Destructure imports when possible (eg. import { foo } from 'bar')
- Use async/await instead of callbacks
- Follow ESLint configuration

## Testing
- Use Jest for unit tests
- Place tests in __tests__ directories or *.test.js files
- Run single tests for performance: npm test -- --testNamePattern="test name"

## Workflow
- Always run tests after making changes
- Check linting before committing
- Use meaningful commit messages