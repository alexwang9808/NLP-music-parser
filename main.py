from find_song import *
from FlagEmbedding import BGEM3FlagModel
from pinecone import Pinecone
from read_songs import get_sentiment


# ----- Step 1: Get user input -----
user_input = input("Enter song name (or 'Song by Artist'): ")
if not user_input:
    print("No input provided.")
    exit()

# ----- Step 2: Determine query + filters -----
if " by " in user_input.lower():
    by_index = user_input.lower().index(" by ")
    song_input = user_input[:by_index].strip()
    artist_input = user_input[by_index + 4:].strip()
    query = f"{song_input} {artist_input}"
    filter_title = song_input.lower()
    filter_artist = artist_input.lower()
else:
    query = user_input
    filter_title = user_input.lower()
    filter_artist = None

print(f"Searching Genius for: '{user_input}'...")

# ----- Step 3: Search Genius -----
results = search_song_results(query, max_results=10)

# ----- Step 4: Filter Results -----
input_words = user_input.lower().split()
filtered_results = []

for res in results:
    title = res["title"].lower()
    artist = res["primary_artist"]["name"].lower()
    combined = f"{title} {artist}"

    if any(word in combined for word in input_words):
        filtered_results.append(res)


# ----- Step 5: Display or exit -----
if not filtered_results:
    print("No matching results found.")
    exit()

print("\nMatching results:")
for i, result in enumerate(filtered_results, 1):
    print(f"{i}. '{result['title']}' by {result['primary_artist']['name']}")

try:
    choice = int(input("\nEnter the number of the song you'd like to see lyrics for (or 0 to cancel): "))
    if 1 <= choice <= len(filtered_results):
        selected = filtered_results[choice - 1]
        title = selected["title"]
        artist = selected["primary_artist"]["name"]
        url = selected["url"]

        print(f"\nFetching lyrics for '{title}' by {artist}...")
        lyrics = scrape_lyrics_from_url(url)
        if lyrics:
            print(f"\nLyrics for '{title}' by {artist}:\n")
            print(lyrics)
        else:
            print("Lyrics not found.")
    else:
        print("Cancelled.")
except ValueError:
    print("Invalid input.")
    
# ----- Step 6: Get vector embedding of song -----
vector_model = BGEM3FlagModel("BAAI/bge-m3")
user_embedding = vector_model.encode(lyrics)["dense_vecs"]


pc = Pinecone(api_key="d521ba70-bedc-4b48-9af8-82dda143a820")
index = pc.Index("nlp-project")
if lyrics:
    # Embed and search
    user_embedding = vector_model.encode(lyrics)["dense_vecs"]
    results = index.query(
    vector=user_embedding.tolist(),
    top_k=20,  # Fetch more to account for duplicates
    namespace="simple",
    include_metadata=True
    )

    seen = set()
    count = 0
    selected_id = (title.lower(), artist.lower())

    print("\nTop 10 most similar songs based on lyrics:")
    for match in results["matches"]:
        meta = match["metadata"]
        song_id = (meta['song'].lower(), meta['artist'].lower())

        if song_id in seen or song_id == selected_id:
            continue

        seen.add(song_id)
        print(f"- '{meta['song']}' by {meta['artist']} (Score: {match['score']:.4f})")
        count += 1

        if count == 10:
            break

# ----- Step 7: Sentiment Analysis -----
    sentiment = get_sentiment(lyrics)
    print("\nSentiment Analysis:")
    print(f"Positive: {sentiment['positive']:.2f}")
    print(f"Neutral: {sentiment['neutral']:.2f}")
    print(f"Negative: {sentiment['negative']:.2f}")
    

