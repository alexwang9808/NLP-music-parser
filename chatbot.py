from find_song import search_song_results, scrape_lyrics_from_url
from read_songs import get_embedding, vector_model, index
from main import parse_query, filter_search_results, plot_similarity_and_sentiment, classify_sentiment
import os

session_state = {
    "mode": None,
    "matches": [],
    "original_input": ""
}


def chatting(user_input):
    if session_state["mode"] == "awaiting_selection":
        try:
            choice = int(user_input.strip())
            matches = session_state["matches"]

            if 1 <= choice <= len(matches):
                selected = matches[choice - 1]
                session_state["mode"] = None
                session_state["matches"] = []

                return handle_selected_song(selected)
            else:
                return "Invalid number. Please enter a number from the list."
        except ValueError:
            return "Please enter a valid number to select a song."

    # Search songs
    query = parse_query(user_input)
    results = search_song_results(query, max_results=10)
    filtered_results = filter_search_results(results, user_input)

    if not filtered_results:
        return "No matching results found."

    # Multiple results
    if len(filtered_results) > 1:
        session_state["mode"] = "awaiting_selection"
        session_state["matches"] = filtered_results
        session_state["original_input"] = user_input

        options = "\n".join(
            [f"{i+1}. '{r['title']}' by {r['primary_artist']['name']}"
             for i, r in enumerate(filtered_results)]
        )
        return f"I found multiple matches for '{user_input}':\n{options}\n\nPlease reply with a number (1–{len(filtered_results)})."

    # Only one match
    selected = filtered_results[0]
    return handle_selected_song(selected)


def handle_selected_song(selected):
    title = selected["title"]
    artist = selected["primary_artist"]["name"]
    url = selected["url"]

    lyrics = scrape_lyrics_from_url(url)
    if not lyrics:
        return f"Lyrics for '{title}' by {artist} not found."

    embedding = get_embedding(lyrics)["dense_vecs"]
    selected_id = (title.lower(), artist.lower())

    response = index.query(
        vector=embedding.tolist(),
        top_k=50,
        namespace="simple",
        include_metadata=True
    )

    plot_similarity_and_sentiment(response["matches"], selected_id)
    top_matches_result = top_similar_songs_helper(response["matches"], selected_id)

    #return (
    #    f"Charts generated for '{title}' by {artist}'.\n\n"
    #    f"Top 10 similar songs:\n{top_matches_result}"
    #)
    return f"Top 10 similar songs:\n{top_matches_result}"


def top_similar_songs_helper(matches, selected_id, top_k=10):
    seen = set()
    lines = []
    count = 0

    for match in matches:
        meta = match["metadata"]
        song_id = (meta["song"].lower(), meta["artist"].lower())
        if song_id in seen or song_id == selected_id:
            continue
        seen.add(song_id)
        lines.append(f"- '{meta['song']}' by {meta['artist']} (Score: {match['score']:.4f})")
        count += 1
        if count == top_k:
            break

    return "\n".join(lines)
