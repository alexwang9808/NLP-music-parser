from FlagEmbedding import BGEM3FlagModel
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm
import numpy as np

model = BGEM3FlagModel("BAAI/bge-m3")

def semantic_chunk_lyrics(lyrics, similarity_threshold=0.75):
    lines = [line.strip() for line in lyrics.split('\n') if line.strip()]
    if len(lines) <= 4:
        return ['\n'.join(lines)]

    # Step 1: Embed each line
    embeddings = [model.encode(line)['dense_vecs'] for line in lines]

    # Step 2: Compute cosine similarity between adjacent lines
    similarities = []
    for i in range(len(embeddings) - 1):
        sim = cosine_similarity([embeddings[i]], [embeddings[i+1]])[0][0]
        similarities.append(sim)

    # Step 3: Determine chunk boundaries
    chunks = []
    current_chunk = [lines[0]]
    for i in range(1, len(lines)):
        if similarities[i-1] >= similarity_threshold:
            current_chunk.append(lines[i])
        else:
            chunks.append('\n'.join(current_chunk))
            current_chunk = [lines[i]]

    chunks.append('\n'.join(current_chunk))  # Final chunk
    return chunks

def chunk_lyrics_semantically(lyrics, window_size=2, similarity_threshold=0.80, max_chunk_lines=6):
    assert window_size in [2, 3], "Only window sizes 2 or 3 are supported."

    # Step 1: Preprocess lines
    lines = [line.strip() for line in lyrics.split("\n") if line.strip()]
    if len(lines) < window_size:
        return ['\n'.join(lines)]  # Not enough lines to chunk

    # Step 2: Create overlapping windows
    windows = ['\n'.join(lines[i:i+window_size]) for i in range(len(lines) - window_size + 1)]

    # Step 3: Embed each window
    embeddings = [model.encode(w)["dense_vecs"] for w in tqdm(windows, desc="Encoding windows")]

    # Step 4: Compute similarity between adjacent windows
    similarities = [
        cosine_similarity([embeddings[i]], [embeddings[i + 1]])[0][0]
        for i in range(len(embeddings) - 1)
    ]

    # Step 5: Create chunks based on similarity threshold
    chunks = []
    current_chunk = [lines[0]]

    for i in range(1, len(lines)):
        current_chunk.append(lines[i])

        # Determine corresponding window similarity (index is i - window_size + 1)
        sim_index = i - window_size + 1
        if sim_index >= 0 and sim_index < len(similarities):
            sim = similarities[sim_index]

            # If similarity is low OR chunk too long → break
            if sim < similarity_threshold or len(current_chunk) >= max_chunk_lines:
                chunks.append('\n'.join(current_chunk))
                current_chunk = []

    # Append remaining lines
    if current_chunk:
        chunks.append('\n'.join(current_chunk))

    return chunks
