# Genius API Setup Guide

## Step 1: Get Your Genius API Token

1. **Go to Genius Developer Portal**: Visit https://genius.com/api-clients

2. **Create/Login to Genius Account**:
   - If you don't have a Genius account, click "Sign Up"
   - If you have an account, click "Sign In"

3. **Create New API Client**:
   - Once logged in, click "New API Client"
   - Fill out the form:
     - **App Name**: "RhymeScheme Analyzer" (or any name you prefer)
     - **App Website URL**: "http://localhost:8080"
     - **Redirect URI**: "http://localhost:8080"
     - **App Description**: "Educational rhyme scheme analysis tool"

4. **Generate Access Token**:
   - After creating the client, click on your app name
   - Click "Generate Access Token" button
   - Copy the generated token (it will look like: `your_long_token_string_here`)

## Step 2: Configure Your Local Environment

1. **Create .env file**: In the RhymeScheme directory, create a file named `.env`

2. **Add your token**: Put this line in the .env file:
   ```
   GENIUS_ACCESS_TOKEN=your_actual_token_here
   ```
   (Replace `your_actual_token_here` with the token you copied from Step 1)

## Step 3: Test the Setup

1. **Start the server**:
   ```bash
   cd RhymeScheme
   source venv/bin/activate
   python app.py
   ```

2. **Look for success message**: You should see:
   ```
   ✓ Genius API initialized successfully
   ```

3. **Test in browser**:
   - Go to http://localhost:8080
   - Try searching for a song like "Lose Yourself" by "Eminem"

## Troubleshooting

- **"No Genius API token found"**: Make sure your .env file is in the right directory and has the correct format
- **"Failed to initialize Genius API"**: Check that your token is valid and copied correctly
- **"No lyrics found"**: Try different search terms or verify the song exists on Genius.com

## Example .env file:
```
GENIUS_ACCESS_TOKEN=AbCdEf123456789...your_actual_token_here
```

That's it! The lyrics search should now work with the official Genius API.