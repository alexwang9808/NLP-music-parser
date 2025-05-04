from find_song import search_song_results, scrape_lyrics_from_url
from read_songs import vector_model, index


def get_user_input():
    user_input = input("Enter song name (or 'Song by Artist'): ").strip()
    if not user_input:
        print("No input provided.")
        exit()
    return user_input


def parse_query(user_input):
    if " by " in user_input.lower():
        by_index = user_input.lower().index(" by ")
        song = user_input[:by_index].strip()
        artist = user_input[by_index + 4:].strip()
        return f"{song} {artist}"
    else:
        return user_input



def filter_search_results(results, user_input):
    input_words = user_input.lower().split()
    filtered = []

    for res in results:
        title = res["title"].lower()
        artist = res["primary_artist"]["name"].lower()
        combined = f"{title} {artist}"

        if any(word in combined for word in input_words):
            filtered.append(res)

    return filtered


def select_song(filtered_results):
    print("\nMatching results:")
    for i, result in enumerate(filtered_results, 1):
        print(f"{i}. '{result['title']}' by {result['primary_artist']['name']}")

    try:
        choice = int(input("\nEnter the number of the song you'd like to see lyrics for (or 0 to cancel): "))
        if 1 <= choice <= len(filtered_results):
            return filtered_results[choice - 1]
        else:
            print("Cancelled.")
            exit()
    except ValueError:
        print("Invalid input.")
        exit()


def embed_and_search(lyrics, selected_title, selected_artist):
    embedding = vector_model.encode(lyrics)["dense_vecs"]

    response = index.query(
        vector=embedding.tolist(),
        top_k=20,
        namespace="simple",
        include_metadata=True
    )

    selected_id = (selected_title.lower(), selected_artist.lower())
    seen = set()
    count = 0

    print("\nTop 10 most similar songs based on lyrics:")
    for match in response["matches"]:
        meta = match["metadata"]
        song_id = (meta["song"].lower(), meta["artist"].lower())

        if song_id in seen or song_id == selected_id:
            continue

        seen.add(song_id)
        print(f"- '{meta['song']}' by {meta['artist']} (Score: {match['score']:.4f})")
        print("Sentiment Analysis:")
        print(f"Positive: {float(meta.get('sentiment_positive', 0)):.2f}")
        print(f"Neutral:  {float(meta.get('sentiment_neutral', 0)):.2f}")
        print(f"Negative: {float(meta.get('sentiment_negative', 0)):.2f}\n")

        count += 1
        if count == 10:
            break


def main():
    user_input = get_user_input()
    query = parse_query(user_input)

    print(f"Searching Genius for: '{user_input}'...")
    results = search_song_results(query, max_results=10)
    filtered_results = filter_search_results(results, user_input)

    if not filtered_results:
        print("No matching results found.")
        return

    selected = select_song(filtered_results)
    title = selected["title"]
    artist = selected["primary_artist"]["name"]
    url = selected["url"]

    print(f"\nFetching lyrics for '{title}' by {artist}...")
    lyrics = scrape_lyrics_from_url(url)

    if lyrics:
        print(f"\nLyrics for '{title}' by {artist}:\n")
        print(lyrics)
        embed_and_search(lyrics, title, artist)
    else:
        print("Lyrics not found.")


if __name__ == "__main__":
    main()
