 # Regular expression module import karna.
import re

# AI generated answer validate karne ka function.
def validate_answer(answer, evidence):

    # Validation issues store karne ke liye list.
    issues = []

    # Valid citations store karne ke liye list.
    valid_citations = []

    # Answer string check karna.
    if not isinstance(answer, str) or not answer.strip():

        # Empty answer par issue add karna.
        issues.append("Generated answer is empty.")

    # Evidence list check karna.
    if not evidence:

        # Evidence missing hone par issue add karna.
        issues.append("No supporting evidence available.")

    # Evidence ke har item ko check karna.
    for item in evidence or []:

        # Evidence metadata extract karna.
        metadata = item.get("metadata", {})

        # Important source identifiers select karna.
        for key in ["asset_id", "chunk_id", "segment_id", "source_id"]:

            # Metadata mein identifier available hai ya nahi.
            identifier = metadata.get(key)

            # Identifier answer mein present hai ya nahi.
            if identifier and re.search(
                r"(?<!\w)" + re.escape(str(identifier)) + r"(?!\w)",
                answer or ""
            ):

                # Supported citation record karna.
                valid_citations.append(str(identifier))

    # Evidence available hai lekin citation mention nahi hui.
    if evidence and not valid_citations:

        # Missing citation warning add karna.
        issues.append("No retrieved evidence identifiers found in answer.")

    # Duplicate citations remove karna.
    valid_citations = list(dict.fromkeys(valid_citations))

    # Final validation result return karna.
    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "valid_citations": valid_citations
    }