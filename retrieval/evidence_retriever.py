from retrieval.query_processor import process_query
from database.chroma_manager import load_database, search_database
from retrieval.evidence_ranker import rank_evidence

def retrieve_evidence(query, k=3, modality_filters=None):
    clean_query = process_query(query)
    vector_store = load_database()
    results = search_database(vector_store, clean_query, k=k, modality_filters=modality_filters)
    evidence = [{"content": doc.page_content, "metadata": doc.metadata, "score": float(score)}
                for doc, score in results]
    return rank_evidence(evidence)
