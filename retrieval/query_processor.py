
import re


# User query ko clean aur prepare karna.
def process_query(query):

    # Query string validate karna.
    if not isinstance(query, str):
        raise TypeError("Query must be a string")

    # Extra spaces remove karna.
    query = query.strip()

    # Multiple spaces ko single space banana.
    query = re.sub(r"\s+", " ", query)

    # Empty query check karna.
    if not query:
        raise ValueError("Query cannot be empty")

    # Clean query return karna.
    return query
