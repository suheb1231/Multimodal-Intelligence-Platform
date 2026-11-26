# Evidence retrieval function import karna.
from retrieval.evidence_retriever import retrieve_evidence

# Retrieval planner import karna.
from agents.retrieval_planner import plan_retrieval

# Synthesis writer import karna.
from agents.synthesis_writer import synthesize_answer

# Gemini initialization function import karna.
from rag.answer_generator import get_llm


# Complete AI assistant workflow.
def run_assistant(question, k=3, llm=None):

    # User query ke liye retrieval plan generate karna.
    retrieval_plan = plan_retrieval(question, k=k)

    # Planner ke modality filters ke according evidence retrieve karna.
    evidence = retrieve_evidence(
        question,
        k=retrieval_plan["top_k"],
        modality_filters=retrieval_plan["modality_filters"]
    )

    # Evidence available hone par Gemini initialize karna.
    if evidence and llm is None:
        llm = get_llm()

    # Synthesis writer se answer generate aur validate karna.
    synthesis_result = synthesize_answer(
        question,
        evidence,
        llm
    )

    # Complete assistant response prepare karna.
    return {
        "question": question,
        "retrieval_plan": retrieval_plan,
        "evidence": evidence,
        "answer": synthesis_result["answer"],
        "validation": synthesis_result["validation"],
        "evidence_count": synthesis_result["evidence_count"],
        "evidence_gaps": synthesis_result["evidence_gaps"],
        "status": synthesis_result["status"]
    }