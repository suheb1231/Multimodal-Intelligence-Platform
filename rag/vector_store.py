from config import FAISS_DIR
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

def create_vector_store(chunks):
    texts = [item["chunk_text"] for item in chunks]
    metadatas = [{k: v for k, v in item.items() if k != "chunk_text"}
                 for item in chunks]
    return FAISS.from_texts(texts=texts, embedding=embeddings_model, metadatas=metadatas)

def save_vector_store(vector_store, path=None):
    target = str(path or FAISS_DIR)
    FAISS_DIR.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(target)

def load_vector_store(path=None):
    target = str(path or FAISS_DIR)
    if not (FAISS_DIR / "index.faiss").exists() and path is None:
        raise FileNotFoundError(f"FAISS index not found at {target}. Process an asset first.")
    return FAISS.load_local(target, embeddings_model, allow_dangerous_deserialization=True)

def search_vector_store(vector_store, query, k=3, modality_filters=None):
    results = vector_store.similarity_search_with_score(
        query, k=k, filter={"modality": {"$in": modality_filters}} if modality_filters else None,
        fetch_k=max(k * 10, 20))
    return results
