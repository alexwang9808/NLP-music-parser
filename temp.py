# import cohere
from pinecone import Pinecone
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain_pinecone import PineconeVectorStore
from custom_embedding import GLMEmbedding2
from FlagEmbedding import FlagReranker


chat = ChatOpenAI(
    openai_api_key="sk-5269f486a3e64ebf8625ecd81f7e4d61",
    openai_api_base="https://api.deepseek.com",
    model="deepseek-chat"
)

pc = Pinecone(api_key="d521ba70-bedc-4b48-9af8-82dda143a820")
index = pc.Index("rag")

reranker = FlagReranker('BAAI/bge-reranker-v2-m3')

# co = cohere.Client("")

embed_model = GLMEmbedding2()

vectorstore = PineconeVectorStore(
    index=index, embedding=GLMEmbedding2()
)


def get_context(query):
    # results = vectorstore.similarity_search(query, 3, namespace="connie")
    # source = '\n'.join([chunk.page_content for chunk in results])
    results = index.query(vector=embed_model.embed_query(query), top_k=5, namespace="connie", include_metadata=True)
    source = [x["metadata"]["text"] for x in results["matches"]]

    source = rerank(query, source)

    prompt = (f"Use the context below to answer the query.\n"
              f"Context:\n"
              f"{source}\n"
              f"Query: {query}")
    # print(prompt)
    return prompt


def rerank(query, results):
    pairs = []
    reranked = []
    for i in results:
        pairs.append((query, i))
    scores = reranker.compute_score(pairs)
    order = sorted(range(len(scores)), key=lambda k: scores[k], reverse=True)
    for i in order:
        reranked.append(results[i])
    return reranked[:3]


def chatting(message):
    ms = [
        SystemMessage(content="You are a real estate, finance, and investment expert."
                              "If the query is not a question, respond without context."),
        HumanMessage(content=get_context(message))
    ]
    bot = chat.invoke(ms)
    return bot.content


'''def rerank(query, results):
    reranked = co.rerank(
        query=query, documents=results, top_n=3, model="rerank-multilingual-v3.0"
    )
    return reranked'''


'''messages = [
    SystemMessage(content="You are a real estate, finance, and investment expert."
                          "If the query is not a question, respond without context.")
]

while True:
    user = input("You: ")
    messages.append(HumanMessage(content=get_context(user)))
    print("AI : ", end="")
    res = chat.invoke(messages)
    print(res.content)
    messages.append(res)
    if len(messages) > 5:
        messages = [messages[0]] + messages[3:]'''