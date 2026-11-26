
# Regular expressions use karne ke liye re import karna.
import re

# Existing query processor import karna.
from retrieval.query_processor import process_query


# Project ki supported modalities define karna.
SUPPORTED_MODALITIES = {
    "pdf": ["pdf", "document", "notes"],
    "video": ["video", "lecture"],
    "audio": ["audio", "recording", "speech"],
    "image": ["image", "picture", "diagram", "chart"],
    "text": ["text", "article"],
    "quiz": ["quiz", "question", "assessment"],
    "discussion": ["discussion", "forum"]
}


# Query se retrieval plan generate karne wala function.
def plan_retrieval(query, k=3):

    # User query ko clean karna.
    clean_query = process_query(query)

    # Top K value positive integer honi chahiye.
    if isinstance(k, bool) or not isinstance(k, int) or k <= 0:
        raise ValueError("k must be a positive integer")

    # Query ko lowercase mein convert karna.
    lower_query = clean_query.lower()

    # Query mein mentioned modalities identify karna.
    selected_modalities = []

    # Har supported modality ko check karna.
    for modality, terms in SUPPORTED_MODALITIES.items():

        # Modality ke keywords ko query mein search karna.
        if any(
            re.search(r"\b" + re.escape(term) + r"\b", lower_query)
            for term in terms
        ):

            # Matching modality ko result mein add karna.
            selected_modalities.append(modality)

    # Common unnecessary words define karna.
    stop_words = {
        "the", "is", "are", "was", "were", "a", "an",
        "and", "or", "of", "in", "on", "to", "for",
        "from", "with", "by", "using", "explain",
        "describe", "show", "me", "please", "what",
        "how", "why", "about"
    }

    # Query ko individual words mein divide karna.
    words = re.findall(r"\b[a-zA-Z0-9]+\b", lower_query)

    # Unnecessary words remove karke keywords prepare karna.
    keywords = [
        word for word in words
        if word not in stop_words
        and not any(
            word in terms
            for terms in SUPPORTED_MODALITIES.values()
        )
    ]

    # Agar keywords empty hain toh original query use karna.
    if not keywords:
        keywords = words

    # Final structured retrieval plan create karna.
    retrieval_plan = {
        "original_query": clean_query,
        "keywords": list(dict.fromkeys(keywords)),
        "modality_filters": selected_modalities,
        "top_k": k,
        "strategy": (
            "modality_filtered"
            if selected_modalities
            else "search_all_modalities"
        )
    }

    # Prepared retrieval plan return karna.
    return retrieval_plan
