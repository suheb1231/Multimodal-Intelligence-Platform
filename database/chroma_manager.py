from rag.vector_store import create_vector_store, save_vector_store, load_vector_store, search_vector_store

def create_database(chunks):
    return create_vector_store(chunks)

def save_database(vector_store):
    save_vector_store(vector_store)

def load_database():
    return load_vector_store()

def search_database(vector_store, query, k=3, modality_filters=None):
    return search_vector_store(vector_store, query, k=k, modality_filters=modality_filters)
