
from sentence_transformers import SentenceTransformer


# Local text embedding model select karna.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# Embedding model load karna.
model = SentenceTransformer(MODEL_NAME)


def generate_text_embeddings(chunks):

    # Har chunk se text extract karna.
    texts = [chunk["chunk_text"] for chunk in chunks]

    # Text ko numerical vectors mein convert karna.
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # Generated embeddings return karna.
    return embeddings
