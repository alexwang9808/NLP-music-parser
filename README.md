============================================================
NLP Song Recommender Chatbot
============================================================

A web-based chatbot that lets users search songs, view lyrics, and discover similar tracks using semantic similarity and sentiment analysis. Built with modern NLP models, vector embeddings, Pinecone indexing, and dynamic chart visualizations.

------------------------------------------------------------
Project Structure
------------------------------------------------------------

app.py----------------# Flask web logic
chatbot.py------------# Chat logic
main.py---------------# CLI version of program (contains all main functions)
index.html------------# Chatbot frontend
find_song.py----------# Genius API + lyrics scraper
read_songs.py---------# Embedding + sentiment utilities
spotify_data.csv------# Dataset of all songs + lyrics
charts/---------------# Location of generated similarity/sentiment visualizations
requirements.txt------# Necessary Python packages (for easy pip install)

------------------------------------------------------------
How to Run
------------------------------------------------------------

1. Clone the repo or download the source files.

2. Install required packages:
   pip install -r requirements.txt

3. To run the web chatbot:
   python app.py
   Then open http://127.0.0.1:5000/ in your browser.

4. (Optional Alternative) 
   To run the CLI chatbot:
   python main.py

------------------------------------------------------------
Features
------------------------------------------------------------

- Input a song name (or 'Song' by 'Artist')
- Automatically searches Genius API to obtain song lyrics
- Embeds lyrics using BGE-M3 FlagEmbedding
- Returns top 10 semantically similar songs
- Analyzes sentiment: positive / neutral / negative
- Generates charts for:
    - Semantic similarity scores
    - Sentiment distribution
- Interactive chatbot interface (Flask + HTML)

------------------------------------------------------------
Requirements
------------------------------------------------------------

Python 3.8+

Main libraries:
- Flask
- requests
- lyricsgenius
- pandas
- matplotlib
- torch
- transformers
- FlagEmbedding
- pinecone-client
- beautifulsoup4

All are listed in `requirements.txt`

------------------------------------------------------------
Notes
------------------------------------------------------------

- HuggingFace models download automatically on first run.
- Ensure spotify_data.csv includes columns: artist, song, text.
- Charts will be saved to the charts/ directory.

------------------------------------------------------------
Names
------------------------------------------------------------

Created by: Aaron Chang, Jichuan Li, Alex Wang
