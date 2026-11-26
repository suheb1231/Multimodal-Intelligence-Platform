
from sentence_transformers import SentenceTransformer


# Local embedding model load kar rahe hain.
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embeddings(chunks):

    # Har chunk ka text extract kar rahe hain.
    texts = [chunk["chunk_text"] for chunk in chunks]

    # Text ko numerical vectors mein convert kar rahe hain.
    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    # Original chunks aur unke embeddings return kar rahe hain.
    return embeddings
