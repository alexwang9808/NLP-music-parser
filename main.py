from find_song import search_song_results, scrape_lyrics_from_url
from read_songs import vector_model, index
import matplotlib.pyplot as plt
from collections import Counter
import os

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
        top_k=50,  # fetch more for sentiment filtering
        namespace="simple",
        include_metadata=True
    )

    selected_id = (selected_title.lower(), selected_artist.lower())
    sentiment_target = None
    seen = set()
    count = 0

    # ---- Top 10 Most Similar Songs ----
    print("\nTop 10 most similar songs based on semantics:")
    for match in response["matches"]:
        meta = match["metadata"]
        song_id = (meta["song"].lower(), meta["artist"].lower())

        if song_id in seen or song_id == selected_id:
            continue

        seen.add(song_id)
        print(f"- '{meta['song']}' by {meta['artist']} (Score: {match['score']:.4f})")

        count += 1
        if count == 10:
            break

    # ---- Get sentiment of selected song (from metadata) ----
    for match in response["matches"]:
        meta = match["metadata"]
        song_id = (meta["song"].lower(), meta["artist"].lower())

        if song_id == selected_id:
            sentiment_target = {
                "positive": float(meta.get("sentiment_positive", 0)),
                "neutral":  float(meta.get("sentiment_neutral", 0)),
                "negative": float(meta.get("sentiment_negative", 0)),
            }
            break

    if not sentiment_target:
        print("Sentiment of selected song not found in metadata.")
        return

    print(f"\nSentiment of '{selected_title}' by {selected_artist}:")
    print(f"Positive: {sentiment_target['positive']:.2f}")
    print(f"Neutral:  {sentiment_target['neutral']:.2f}")
    print(f"Negative: {sentiment_target['negative']:.2f}\n")

    # ---- Call sentiment-matching filter ----
    print("Filter songs by sentiment:")
    print("1. Show similar sentiment songs")
    print("2. Show opposite sentiment songs")
    print("3. Show both")
    print("4. Skip")
    choice = input("Enter 1/2/3/4: ").strip()
    plot_similarity_and_sentiment(response["matches"], selected_id)

    
    if choice == "1":
        sentiment(response["matches"], selected_id, sentiment_target)
    elif choice == "2":
        opposite_sentiment(response["matches"], selected_id, sentiment_target)
    elif choice == "3":
        sentiment(response["matches"], selected_id, sentiment_target)
        opposite_sentiment(response["matches"], selected_id, sentiment_target)
    else:
        print("Skipping sentiment filtering.")



def sentiment(similar_matches, selected_id, sentiment_target):
    print("\nTop similar songs with matching sentiment:")
    count = 0
    seen = set()

    for match in similar_matches:
        meta = match["metadata"]
        song_id = (meta["song"].lower(), meta["artist"].lower())

        if song_id in seen or song_id == selected_id:
            continue

        if abs(meta.get("sentiment_positive", 0) - sentiment_target["positive"]) < 0.06 and \
           abs(meta.get("sentiment_neutral", 0) - sentiment_target["neutral"]) < 0.06 and \
           abs(meta.get("sentiment_negative", 0) - sentiment_target["negative"]) < 0.06:

            seen.add(song_id)
            print(f"- '{meta['song']}' by {meta['artist']} (Score: {match['score']:.4f})")
            print("Sentiment Match:")
            print(f"  Positive: {float(meta.get('sentiment_positive', 0)):.2f}")
            print(f"  Neutral:  {float(meta.get('sentiment_neutral', 0)):.2f}")
            print(f"  Negative: {float(meta.get('sentiment_negative', 0)):.2f}\n")

            count += 1
            if count == 10:
                break

    if count == 0:
        print("No similar songs with matching sentiment found.")

    
def is_opposite_sentiment(meta, sentiment_target, threshold=0.4):
    return (
        (sentiment_target['positive'] > 0.6 and meta.get('sentiment_negative', 0) > threshold) or
        (sentiment_target['negative'] > 0.6 and meta.get('sentiment_positive', 0) > threshold)
    )
    
def opposite_sentiment(similar_matches, selected_id, sentiment_target):
    print("\nTop similar songs but with opposite sentiment:")
    count = 0
    seen = set()

    for match in similar_matches:
        meta = match["metadata"]
        song_id = (meta["song"].lower(), meta["artist"].lower())

        if song_id in seen or song_id == selected_id:
            continue

        if is_opposite_sentiment(meta, sentiment_target):
            seen.add(song_id)
            print(f"- '{meta['song']}' by {meta['artist']} (Score: {match['score']:.4f})")
            print("Sentiment:")
            print(f"  Positive: {float(meta.get('sentiment_positive', 0)):.2f}")
            print(f"  Neutral:  {float(meta.get('sentiment_neutral', 0)):.2f}")
            print(f"  Negative: {float(meta.get('sentiment_negative', 0)):.2f}\n")

            count += 1
            if count == 10:
                break

    if count == 0:
        print("No similar songs with opposite sentiment found.")


def classify_sentiment(meta):
    pos = meta.get("sentiment_positive", 0)
    neg = meta.get("sentiment_negative", 0)
    if pos > 0.6:
        return "Positive"
    elif neg > 0.6:
        return "Negative"
    else:
        return "Neutral"

def plot_similarity_and_sentiment(matches, selected_id, output_dir="charts"):
    os.makedirs(output_dir, exist_ok=True)

    similarity_labels = []
    similarity_scores = []
    sentiment_classes = []

    seen = set()
    count = 0

    for match in matches:
        meta = match["metadata"]
        song_id = (meta["song"].lower(), meta["artist"].lower())

        if song_id == selected_id or song_id in seen:
            continue

        seen.add(song_id)
        label = f"‘{meta['song']}’ by {meta['artist']}"
        similarity_labels.append(label)
        similarity_scores.append(match["score"])
        sentiment_classes.append(classify_sentiment(meta))

        count += 1
        if count == 10:
            break

    # --- Similarity Chart ---
    plt.figure(figsize=(10, 5))
    bars = plt.barh(similarity_labels[::-1], similarity_scores[::-1], color="#1f77b4")
    plt.xlabel("Similarity Score")
    plt.title("Top 10 Most Similar Songs by Semantic Embedding")
    plt.xlim(0, 1.0)  # fix x-axis range

    plt.tight_layout()
    similarity_path = os.path.join(output_dir, "similarity_chart.png")
    plt.savefig(similarity_path)
    plt.close()
    print(f"✅ Saved similarity chart to {similarity_path}")

    # --- Sentiment Distribution Chart ---
    sentiment_counts = Counter(sentiment_classes)
    sentiment_labels = ["Positive", "Neutral", "Negative"]
    sentiment_values = [sentiment_counts.get(label, 0) for label in sentiment_labels]

    plt.figure(figsize=(6, 4))
    bars = plt.bar(sentiment_labels, sentiment_values, color=["green", "gray", "red"])
    plt.title("Sentiment Distribution of Top 10 Similar Songs")
    plt.ylabel("Number of Songs")
    plt.ylim(0, max(sentiment_values) + 1)

    # Add count labels to bars
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, height + 0.2, str(int(height)),
             ha='center', fontsize=10)

    plt.tight_layout(rect=[0, 0, 1, 0.95])  # reserves space for the title
    sentiment_path = os.path.join(output_dir, "sentiment_distribution.png")
    plt.savefig(sentiment_path)
    plt.close()
    print(f"✅ Saved sentiment chart to {sentiment_path}")



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
