import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from torch.nn.functional import softmax
from FlagEmbedding import BGEM3FlagModel
from pinecone import Pinecone
from tqdm import tqdm

model_name = "cardiffnlp/twitter-roberta-base-sentiment"
sentiment_model = AutoModelForSequenceClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

def get_sentiment(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = sentiment_model(**inputs)
    probs = softmax(outputs.logits, dim=1)
    classes = ['negative', 'neutral', 'positive']
    scores = {cls: float(probs[0][i]) for i, cls in enumerate(classes)}
    return scores

if __name__ == "__main__":
    df = pd.read_csv("spotify_data.csv", delimiter=',', on_bad_lines='error')


    vector_model = BGEM3FlagModel("BAAI/bge-m3")

    pc = Pinecone(api_key="d521ba70-bedc-4b48-9af8-82dda143a820")
    index = pc.Index("nlp-project")




    def get_embedding(text):
        return vector_model.encode(text)


    batch = []
    chunk_id = 21000
    for i in tqdm(range(21000, len(df))):
        lyrics = df["text"].iloc[i]
        sentiment = get_sentiment(lyrics)
        vector = get_embedding(lyrics)["dense_vecs"]
        metadata = {
            "artist": df["artist"].iloc[i],
            "song": df["song"].iloc[i],
            "lyrics": lyrics,
            "sentiment_positive": sentiment["positive"],
            "sentiment_neutral": sentiment["neutral"],
            "sentiment_negative": sentiment["negative"],
        }
        batch.append({
            "id": str(chunk_id),
            "values": vector,
            "metadata": metadata
        })
        chunk_id += 1
        if len(batch) == 100:
            index.upsert(vectors=batch, namespace="simple")
            batch = []

    if batch:
        index.upsert(vectors=batch, namespace="simple")
