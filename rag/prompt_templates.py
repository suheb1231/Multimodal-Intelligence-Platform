
# LangChain prompt template import karna.
from langchain_core.prompts import ChatPromptTemplate


# System prompt define karna.
SYSTEM_PROMPT = """
ROLE:
You are a Coursera Multimodal Learning Assistant.

TASK:
Analyze the learner's question using the supplied evidence.
Explain learning difficulties and suggest useful recommendations.

EVIDENCE:
Use only the structured evidence provided below.
Each evidence item may contain content, metadata and distance score.

CONSTRAINTS:
1. Never create unsupported facts.
2. Do not use knowledge outside the supplied evidence.
3. Preserve source IDs and segment IDs.
4. Mention timestamps and modality when available.
5. If evidence is insufficient, clearly say so.
6. Recommendations must be actionable.
7. Final decisions belong to a human reviewer.

OUTPUT SCHEMA:
Return a structured response containing:

answer:
A clear answer to the learner's question.

friction_explanation:
Explain the identified learning difficulty.

recommendations:
Provide practical recommendations.

citations:
List supporting source IDs, segment IDs and timestamps.

evidence_gaps:
Mention missing or insufficient evidence.

VALIDATION:
Every factual claim must be supported by supplied evidence.
Never invent citations or metadata.
"""


# Human prompt define karna.
HUMAN_PROMPT = """
LEARNER QUESTION:
{question}

RETRIEVED EVIDENCE:
{evidence}

Analyze the question and return the required structured response.
"""


# System aur human prompts ko combine karna.
PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", HUMAN_PROMPT)
    ]
)


# Final prompt prepare karne ka function.
def create_prompt(question, evidence):

    # Question aur evidence ko prompt mein insert karna.
    prompt = PROMPT_TEMPLATE.invoke(
        {
            "question": question,
            "evidence": evidence
        }
    )

    # Prepared prompt return karna.
    return prompt
