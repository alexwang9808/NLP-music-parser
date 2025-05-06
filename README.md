NLP Song Recommender Chatbot
============================================================

A web-based chatbot that lets users search songs, view lyrics, and discover similar tracks using semantic similarity and sentiment analysis. Built with modern NLP models, vector embeddings, Pinecone indexing, and dynamic chart visualizations.

![image](https://github.com/user-attachments/assets/a17ad412-e0a5-492b-a1d2-51053d3902cc)

------------------------------------------------------------
Project Structure
------------------------------------------------------------

app.py                 # Flask web logic

chatbot.py             # Chat interaction logic

main.py                # CLI version of the program (contains all main functions)

index.html             # Chatbot frontend UI

find_song.py           # Genius API + lyrics scraper

read_songs.py          # Embedding + sentiment utilities

spotify_data.csv       # Dataset of all songs + lyrics

charts/                # Location of generated similarity/sentiment visualizations

requirements.txt       # Python packages for easy installation (pip install -r)


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
Visualizations
------------------------------------------------------------
![image](https://github.com/user-attachments/assets/4d0af42f-2860-4b9d-92e7-f440cdd3f9c4)
![image](https://github.com/user-attachments/assets/29016c7a-f889-4cbd-8d7a-bd22654de16b)

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
Contributors
------------------------------------------------------------

Created by: Aaron Chang, Jichuan Li, Alex Wang
