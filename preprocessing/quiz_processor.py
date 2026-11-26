
import json  # Quiz data read karne ke liye.
from pathlib import Path  # File paths handle karne ke liye.


def process_quiz(quiz_path, asset_id):  # Quiz preprocessing function.

    quiz_path = Path(quiz_path)  # File path convert kar rahe hain.

    if not quiz_path.exists():  # Check kar rahe hain file available hai ya nahi.
        raise FileNotFoundError(f"Quiz file not found: {quiz_path}")  # File missing hone par error.

    quiz_data = json.loads(quiz_path.read_text(encoding="utf-8"))  # JSON quiz data read kar rahe hain.

    questions = []  # Processed questions store karne ke liye.

    seen = set()  # Duplicate questions track karne ke liye.

    for index, item in enumerate(quiz_data["questions"], start=1):  # Har question process kar rahe hain.

        question = item["question"].strip()  # Question ke extra spaces remove kar rahe hain.

        if question and question.lower() not in seen:  # Empty aur duplicate questions skip kar rahe hain.

            seen.add(question.lower())  # Question ko duplicate tracking mein add kar rahe hain.

            questions.append({
                "asset_id": asset_id,  # Original quiz ki ID.
                "segment_id": f"{asset_id}-QUESTION-{len(questions) + 1}",  # Unique question ID.
                "source_file": quiz_path.name,  # Original quiz filename.
                "question": question,  # Clean question.
                "options": item.get("options", []),  # Question ke options.
                "correct_answer": item.get("correct_answer"),  # Correct answer.
                "modality": "quiz"  # Asset modality define kar rahe hain.
            })

    return questions  # Processed quiz questions return kar rahe hain.
