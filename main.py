import lyricsgenius
import difflib

genius_api_token = "i0hXzddGbJLbNBLiJ7F8VM430P2mv_maQBFw48U7g4cP4wpw5QJPIBczcksGXUFy"
genius = lyricsgenius.Genius(genius_api_token, remove_section_headers=True, verbose=False)

def fuzzy_match_song(song_title, artist_name, max_songs=5):
    artist = genius.search_artist(artist_name, max_songs=max_songs, get_full_info=False)
    if not artist or not artist.songs:
        return []

    top_songs = [(song.title.strip(), song) for song in artist.songs]
    titles = [title for title, _ in top_songs]
    matches = difflib.get_close_matches(song_title, titles, n=2, cutoff=0.3)  # Top 2 from artist

    return [(title, song_obj) for title, song_obj in top_songs if title in matches]

def fuzzy_match_global(song_title, max_results=10):
    results = genius.search(song_title, per_page=max_results)["hits"]
    all_titles = []
    title_map = {}

    for hit in results:
        result = hit["result"]
        title = result["title"]
        artist = result["primary_artist"]["name"]
        combo = f"{title} by {artist}"
        all_titles.append(combo)
        title_map[combo] = (title, artist)

    best_matches = difflib.get_close_matches(song_title, all_titles, n=3, cutoff=0.3)
    return [title_map[match] for match in best_matches]

# ----- Step 1: Get user input -----
user_input = input("Enter song name (or 'Song by Artist'): ").strip()

# ----- Step 2: Try exact match -----
song_title = user_input
artist_name = None
song = None

if " by " in user_input.lower():
    by_index = user_input.lower().index(" by ")
    song_title = user_input[:by_index].strip()
    artist_name = user_input[by_index + 4:].strip()
    print(f"Searching for '{song_title}' by '{artist_name}'...")
    song = genius.search_song(song_title, artist_name)
else:
    print(f"Searching for '{song_title}'...")
    song = genius.search_song(song_title)

# ----- Step 3: Handle result -----
if song:
    print(f"Found: '{song.title}' by {song.artist}\n")
    print(song.lyrics)
else:
    artist_matches = []
    global_matches = []

    if artist_name:
        artist_matches = fuzzy_match_song(song_title, artist_name)
    global_matches = fuzzy_match_global(user_input)

    combined_options = []

    # Add artist-based matches (top 2)
    for title, song_obj in artist_matches:
        combined_options.append((title, song_obj.artist, song_obj))

    # Add global matches (next 3)
    for title, artist in global_matches:
        combined_options.append((title, artist, None))

    if combined_options:
        print("\nClosest matches:")
        for i, (title, artist, _) in enumerate(combined_options, 1):
            print(f"{i}. '{title}' by {artist}")
        try:
            choice = int(input("\nEnter the number of the song you'd like to see lyrics for (or 0 to cancel): "))
            if 1 <= choice <= len(combined_options):
                selected = combined_options[choice - 1]
                if selected[2]:  # We already have the song object
                    song = selected[2]
                else:
                    # Search again to fetch full song and lyrics
                    song = genius.search_song(selected[0], selected[1])

                if song:
                    print(f"\nLyrics for '{song.title}' by {song.artist}:\n")
                    print(song.lyrics)
                else:
                    print("Lyrics not found.")
            else:
                print("Cancelled.")
        except ValueError:
            print("Invalid input.")
    else:
        print("No similar songs found.")
