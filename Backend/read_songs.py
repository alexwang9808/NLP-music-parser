import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax
from FlagEmbedding import BGEM3FlagModel
from pinecone import Pinecone
from tqdm import tqdm
import re

model_name = "cardiffnlp/twitter-roberta-base-sentiment"
sentiment_model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
vector_model = BGEM3FlagModel("BAAI/bge-m3")

pc = Pinecone(api_key="d521ba70-bedc-4b48-9af8-82dda143a820")
index = pc.Index("nlp-project")

def get_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
    outputs = sentiment_model(**inputs)
    probs = softmax(outputs.logits, dim=1)
    classes = ['negative', 'neutral', 'positive']
    return {cls: float(probs[0][i]) for i, cls in enumerate(classes)}


def get_embedding(text):
    return vector_model.encode(text)


if __name__ == "__main__":
    df = pd.read_csv("Data/spotify_data.csv", delimiter=',', on_bad_lines='error')
    batch = []

    for i in tqdm(range(len(df))):
        lyrics = df["text"].iloc[i]
        # sentiment = get_sentiment(lyrics)
        raw_chunks = re.split(r'\n\s*\n', lyrics.strip())
        chunks = [chunk.strip() for chunk in raw_chunks if chunk.strip()]

        for j, chunk in enumerate(chunks):
            vector = get_embedding(chunk)["dense_vecs"]
            metadata = {
                "artist": df["artist"].iloc[i],
                "song": df["song"].iloc[i],
                "chunk_id": j,
                "chunk": chunk,
                # "sentiment_positive": sentiment["positive"],
                # "sentiment_neutral": sentiment["neutral"],
                # "sentiment_negative": sentiment["negative"],
            }
            batch.append({
                "id": f"{i}-{j}",
                "values": vector,
                "metadata": metadata
            })

        if len(batch) >= 100:
            print("upsert")
            index.upsert(vectors=batch, namespace="chunked")
            batch = []

    if batch:
        index.upsert(vectors=batch, namespace="chunked")