from find_song import search_song_results, scrape_lyrics_from_url
from read_songs import vector_model, index
from main import parse_query, filter_search_results, plot_similarity_and_sentiment, classify_sentiment
import os

def chatting(user_input):
    query = parse_query(user_input)
    results = search_song_results(query, max_results=10)
    filtered_results = filter_search_results(results, user_input)

    if not filtered_results:
        return "No matching results found."

    selected = filtered_results[0]  # just use first match for web
    title = selected["title"]
    artist = selected["primary_artist"]["name"]
    url = selected["url"]

    lyrics = scrape_lyrics_from_url(url)
    if not lyrics:
        return f"Lyrics for '{title}' by {artist} not found."

    embedding = vector_model.encode(lyrics)["dense_vecs"]

    response = index.query(
        vector=embedding.tolist(),
        top_k=50,
        namespace="simple",
        include_metadata=True
    )

    selected_id = (title.lower(), artist.lower())
    plot_similarity_and_sentiment(response["matches"], selected_id, output_dir="charts")

    return f"Charts generated for '{title}' by {artist}'. See /charts/ folder."
