from find_song import *

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
