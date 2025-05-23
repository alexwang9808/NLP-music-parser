NLP Song Recommender Chatbot
============================================================

A web-based chatbot that lets users search songs, view lyrics, and discover similar tracks using semantic similarity and sentiment analysis. Built with modern NLP models, vector embeddings, Pinecone indexing, and dynamic chart visualizations.

![image](https://github.com/user-attachments/assets/398492ae-b773-4864-85fa-46bffa50df11)

------------------------------------------------------------
Project Structure
------------------------------------------------------------

app.py                 # Flask web logic

chatbot.py             # Chat interaction logic

main.py                # contains all main functions

Frontend/
index.html             # Chatbot frontend UI

Backend/find_song.py   # Genius API + lyrics scraper

Backend/read_songs.py  # Embedding + sentiment utilities

Backend/chunk.py       # Handles chunking logic

Backend/chunk_lyrics.py# Handles chunking logic (copy for testing)

Data/
spotify_data.csv       # Dataset of all songs, artists, lyrics

charts/                # Location of generated similarity/sentiment visualizations

requirements.txt       # Python packages for easy installation (pip install -r)

Report.pdf             # Project report

------------------------------------------------------------
Overview
------------------------------------------------------------

1. Data Collection
    - Acquired a dataset of 57,650 songs from Spotify Million Song Dataset (https://www.kaggle.com/datasets/notshrirang/spotify-million-song-dataset).
    - Each song was preprocessed to generate vector embeddings and sentiment metadata, which were stored in a Pinecone vector database.
2. Song searching through Genius API
    - We used the Genius API to retrieve up to 10 matching results based on a user-inputted song name.
    - This disambiguates songs with common titles or multiple versions.
3. Vector Similarity Matching
    - We used BAAI's BGE-M3 model: (https://huggingface.co/BAAI/bge-m3).
    - It returns the top 10 most semantically similar songs based on cosine similarity.
4. Sentiment Analysis
    - We used CardiffNLP's Twitter RoBERTa model, trained on 58M tweets: (https://huggingface.co/cardiffnlp/twitter-roberta-base-sentiment).
    - Each song is classified as positive, neutral, or negative, enabling sentiment-based recommendations such as similar or opposite moods.
5. Interactive Chatbot
    - Integrated a web-based chatbot using the OpenAI GPT-4o API.
    - The chatbot guides users through the search and recommendation process and dynamically adjusts based on user sentiment preferences.

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
- openai

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
Demo
------------------------------------------------------------
https://youtu.be/l88OfJhWgq0
------------------------------------------------------------
Contributors
------------------------------------------------------------

Created by: Aaron Chang, Jichuan Li, Alex Wang
