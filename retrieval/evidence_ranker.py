
# Evidence ranking function.
def rank_evidence(evidence):

    # Empty evidence check karna.
    if not evidence:
        return []

    # FAISS L2 distance mein lower score better hota hai.
    ranked_evidence = sorted(
        evidence,
        key=lambda item: item["score"]
    )

    # Ranked evidence return karna.
    return ranked_evidence
