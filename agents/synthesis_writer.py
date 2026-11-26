
# Existing RAG answer generator import karna.
from rag.answer_generator import generate_answer

# Existing quality validator import karna.
from agents.quality_validator import validate_answer


# Evidence ke basis par final answer generate karna.
def synthesize_answer(question, evidence, llm):

    # Existing RAG generator se answer generate karna.
    generated_result = generate_answer(
        question,
        evidence,
        llm
    )

    # Check karna ki generator ne dictionary return ki hai.
    if isinstance(generated_result, dict):

        # Dictionary se generated answer extract karna.
        answer = generated_result.get("answer", "")

        # Generator se available evidence gaps extract karna.
        evidence_gaps = generated_result.get("evidence_gaps")

    else:

        # Direct AI response ko answer variable mein store karna.
        answer = generated_result

        # Evidence gaps available nahi hain.
        evidence_gaps = None

    # Existing validator se answer ki quality check karna.
    validation = validate_answer(
        answer,
        evidence
    )

    # Final structured synthesis result create karna.
    result = {
        "question": question,
        "answer": answer,
        "evidence_count": len(evidence or []),
        "validation": validation,
        "evidence_gaps": evidence_gaps,
        "status": (
            "validated"
            if validation["is_valid"]
            else "needs_review"
        )
    }

    # Final result return karna.
    return result
