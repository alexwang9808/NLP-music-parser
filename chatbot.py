from find_song import search_song_results, scrape_lyrics_from_url
from read_songs import get_embedding, index, get_sentiment
from main import parse_query, filter_search_results, sentiment, opposite_sentiment
from openai import OpenAI

model_name = "gpt-4o"

session_state = {
    "mode": None,
    "matches": [],
    "original_input": "",
    "selected": None
}

def chatbot_chat(message, prompt):
    try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system",
                     "content": prompt},
                    {"role": "user",
                     "content": message}
                ],
                stream=False
            )
            return response.choices[0].message.content
    except Exception as e:
        print("GPT error:", e)
        return "Oops, something went wrong with the assistant."


def chatting(user_input):
    if session_state["mode"] == "sentiment":
        choice = int(user_input.strip())
        song_results = handle_selected_song(session_state["selected"])
        selected_id = (session_state["selected"]["title"].lower(), session_state["selected"]["primary_artist"]["name"].lower())
        sentiment_target = get_sentiment(scrape_lyrics_from_url(session_state["selected"]["url"]))
        if choice == 1:
            similar = sentiment(song_results, selected_id, sentiment_target)
            return chatbot_chat(
                f"The user selected to see songs with a similar emotional tone. "
                f"Here are the results:\n{similar}",
                "You are a helpful and friendly music assistant. Introduce the following list of songs warmly, "
                "mention that they share a similar mood or vibe with the user's selected song, and invite them to explore."
                "Provide genius link for each song in this format: <a href='link' target='_blank'>name of song</a>"
                "At the end, give them the option to try the other 3 list items which you number: similar sentiment again, opposite sentiment, or skip."
                "Present the list to the user in a friendly way with no emojis, and clearly ask them to pick one by replying with a number."
            )
        elif choice == 2:
            opposite = opposite_sentiment(song_results, selected_id, sentiment_target)
            return chatbot_chat(
                f"The user asked for emotionally contrasting songs. "
                f"Here are the results:\n{opposite}",
                "You are a fun, music-savvy assistant. Present this list as a mood switch from the user's original song, "
                "maybe describe it as a playlist flip or emotional contrast."
                "Provide genius link for each song in this format: <a href='link' target='_blank'>name of song</a>"
                "At the end, give them the option to try the 3 list items which you number: similar sentiment, opposite sentiment again, or skip."
                "Present the list to the user in a friendly way with no emojis, and clearly ask them to pick one by replying with a number."
            )
        elif choice == 3:
            session_state["mode"] = None
            session_state["selected"] = None
            return chatbot_chat(
                "The user skipped the sentiment filtering option.",
                "Say 'No problem!' and gently prompt the user to tell you another song they would like to explore."
            )
        else:
            return chatbot_chat("The user input an invalid number.",
                                "Politely ask the user to try a number from the list.")

    if session_state["mode"] == "awaiting_selection":
        try:
            choice = int(user_input.strip())
            matches = session_state["matches"]

            if 1 <= choice <= len(matches):
                session_state["selected"] = matches[choice - 1]
                session_state["mode"] = "sentiment"
                session_state["matches"] = []

                # return handle_selected_song(selected)
                song_results = handle_selected_song(session_state["selected"])
                song_result = top_similar_songs_helper(song_results, (session_state["selected"]["title"].lower(), session_state["selected"]["primary_artist"]["name"].lower()))
                return chatbot_chat(f"The user selected option {choice}. Here's the result:\n{song_result}.",
                                    "You are a helpful assistant that explains song recommendations in a warm way. Avoid emojis."
                                    "Provide genius link for each song in this format: <a href='link' target='_blank'>name of song</a>"
                                    "At the end, give them the option to filter by sentiment with 3 list items:"
                                    "similar sentiment, opposite sentiment, or skip."
                                    "Present the list to the user in a friendly way with no emojis, and clearly ask them to pick one by replying with a number.")
            else:
                # return "Invalid number. Please enter a number from the list."
                return chatbot_chat("The user input an invalid number.",
                                    "Politely ask the user to try a number from the list.")
        except ValueError:
            # return "Please enter a valid number to select a song."
            return chatbot_chat("The user typed something that's not a number.",
                                "Remind them to reply with a number from the list.")

    song_input = chatbot_chat(user_input,
                              "You are a precise extraction tool, not a creative assistant."
                              "Extract the song title from the user's input. If the user explicitly mentions an artist, include it in the format: '<Song Title> by <Artist>'."
                              "If the artist is not clearly stated by the user, do NOT guess it."
                              "If a song title cannot be confidently found, return 'None'."
                              "Your answer must only be the result string and nothing else.")

    print(song_input)

    # Search songs
    query = parse_query(song_input)
    results = search_song_results(query, max_results=10)
    filtered_results = filter_search_results(results, user_input)

    if not filtered_results:
        # return "No matching results found."
        return chatbot_chat(
            f"No matches found for '{user_input}'.",
            "Apologize kindly and suggest they try a different song or phrase."
        )

    # Multiple results
    if len(filtered_results) > 1:
        session_state["mode"] = "awaiting_selection"
        session_state["matches"] = filtered_results
        session_state["original_input"] = user_input

        options = "\n".join(
            [f"{i+1}. '{r['title']}' by {r['primary_artist']['name']}"
             for i, r in enumerate(filtered_results)]
        )
        # return f"I found multiple matches for '{user_input}':\n{options}\n\nPlease reply with a number (1–{len(filtered_results)})."
        return chatbot_chat(
            f"I found multiple matches for '{user_input}':\n{options}\n\nPlease reply with a number.",
            "Present the list to the user in a friendly way with no emojis, and clearly ask them to pick one by replying with a number."
        )

    # Only one match
    session_state["selected"] = filtered_results[0]
    session_state["mode"] = None
    session_state["matches"] = []
    # return handle_selected_song(selected)
    song_results = handle_selected_song(session_state["selected"])
    song_result = top_similar_songs_helper(song_results, (session_state["selected"]["title"].lower(), session_state["selected"]["primary_artist"]["name"].lower()))
    return chatbot_chat(
        f"The user searched for '{user_input}' and found one match. Here's the result:\n{song_result}",
        "You are a helpful assistant. Reword the song recommendation results in a friendly and expressive way. Avoid emojis."
        "Provide genius link the song in this format: <a href='link' target='_blank'>name of song</a>"
    )


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

    # plot_similarity_and_sentiment(response["matches"], selected_id)
    # top_matches_result = top_similar_songs_helper(response["matches"], selected_id)

    #return (
    #    f"Charts generated for '{title}' by {artist}'.\n\n"
    #    f"Top 10 similar songs:\n{top_matches_result}"
    #)
    # return f"Top 10 similar songs:\n{top_matches_result}"
    return response["matches"]


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
