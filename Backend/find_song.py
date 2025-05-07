import requests
from bs4 import BeautifulSoup
import lyricsgenius
import re

genius_api_token = "dpNORtcXZRRerdv16ABRj1p7H6L4Lg7eBLAeJFo1K3I1krbZWd4gjBk4kpXL0iXr"
genius = lyricsgenius.Genius(genius_api_token, verbose=False)
genius.timeout = 5


def scrape_lyrics_from_url(url):
    try:
        page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.text, "html.parser")
        lyrics_divs = soup.find_all("div", {"data-lyrics-container": "true"})

        # Combine all divs into one string
        raw_lyrics = "\n".join(div.get_text(separator="\n").strip() for div in lyrics_divs)

        # Split into lines
        lines = raw_lyrics.strip().splitlines()

        # Find start of actual lyrics (skipping junk)
        start_index = 0
        for i, line in enumerate(lines):
            if line.startswith("[") or (len(line.strip()) > 0 and any(word in line.lower() for word in ["verse", "chorus", "intro", "outro", "bridge"])):
                start_index = i
                break
        lines = lines[start_index:]

        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # if not line:
            #     continue  # Skip all blank lines
            if re.match(r"^\[.*?\]$", line):
                continue  # Skip all section headers like [Chorus]
            cleaned_lines.append(line)

        return "\n".join(cleaned_lines).strip()

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
