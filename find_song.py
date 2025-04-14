import requests
from bs4 import BeautifulSoup
import lyricsgenius

genius_api_token = "YOUR_GENIUS_API_TOKEN"
genius = lyricsgenius.Genius(genius_api_token, verbose=False)
genius.timeout = 5

def scrape_lyrics_from_url(url):
    try:
        page = requests.get(url, timeout=5)
        soup = BeautifulSoup(page.text, "html.parser")
        lyrics_divs = soup.find_all("div", {"data-lyrics-container": "true"})
        lyrics = "\n".join([div.get_text(separator="\n").strip() for div in lyrics_divs])
        return lyrics.strip()
    except Exception as e:
        print(f"Error scraping lyrics: {e}")
        return None

def search_song_results(query, max_results=10):
    try:
        hits = genius.search(query, per_page=max_results)["hits"]
        return [hit["result"] for hit in hits]
    except Exception as e:
        print(f"Search failed: {e}")
        return []

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
