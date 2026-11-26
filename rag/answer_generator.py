
# Environment variables access karna.
import os

# .env file se API key load karna.
from dotenv import load_dotenv

# Gemini model import karna.
from langchain_google_genai import ChatGoogleGenerativeAI

# Prompt creation function import karna.
from rag.prompt_templates import create_prompt


# Environment variables load karna.
load_dotenv()


# Gemini LLM initialize karne ka function.
def get_llm():

    # API key environment se read karna.
    api_key = os.getenv("GEMINI_API_KEY")

    # API key missing hone par error dena.
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env")

    # Gemini model initialize karna.
    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=api_key,
        temperature=0
    )

    # Initialized model return karna.
    return llm


# GenAI answer generation function.

# Gemini response content ko plain text mein convert karna.
def _content_to_text(content):

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, str):
                parts.append(item)

            elif isinstance(item, dict):
                text_part = item.get("text")
                if text_part:
                    parts.append(str(text_part))

            else:
                text_part = getattr(item, "text", None)
                if text_part:
                    parts.append(str(text_part))

        return "\n".join(parts)

    if content is None:
        return ""

    return str(content)


# GenAI answer generation function.
def generate_answer(question, evidence, llm):

    # Empty evidence check karna.
    if not evidence:
        return {
            "answer": "Insufficient evidence to answer this question.",
            "evidence_gaps": "No relevant evidence was retrieved."
        }

    # Structured prompt prepare karna.
    prompt = create_prompt(question, evidence)

    # LLM se answer generate karna.
    response = llm.invoke(prompt)

    # AI response content extract karna.
    content = getattr(response, "content", response)

    # Response ko plain text mein normalize karna.
    answer = _content_to_text(content)

    # Structured result return karna.
    return {
        "answer": answer,
        "evidence_gaps": None
    }
