# backend/utils/groq_agent.py

import os
from typing import List, Union, Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Set it in your .env file or environment variables.")

client = Groq(api_key=GROQ_API_KEY)


def generate_student_report(results: List[Union[Dict[str, Any], Any]]) -> str:
    if not results:
        return "No results available to generate a report."

    terms_data = {}
    student_name = None
    term_order = {"First Term": 1, "Second Term": 2, "Third Term": 3}

    for r in results:
        name = getattr(r, "name", None) or (r.get("name") if isinstance(r, dict) else None)
        subject = getattr(r, "subject", None) or (r.get("subject") if isinstance(r, dict) else None)
        percentage = getattr(r, "percentage", None) or (r.get("percentage") if isinstance(r, dict) else None)
        term = getattr(r, "term", None) or (r.get("term") if isinstance(r, dict) else None)
        session = getattr(r, "session", None) or (r.get("session") if isinstance(r, dict) else None)
        total_subjects = getattr(r, "total_subjects", None) or (r.get("total_subjects") if isinstance(r, dict) else None)

        if not student_name and name:
            student_name = name

        if term not in terms_data:
            terms_data[term] = {"subjects": [], "scores": [], "total_subjects": total_subjects, "session": session}

        if subject and percentage is not None:
            terms_data[term]["subjects"].append(f"{subject}: {percentage}%")
            terms_data[term]["scores"].append(percentage)

    sorted_terms = sorted(terms_data.keys(), key=lambda t: term_order.get(t, 0))
    full_report = []

    system_prompt = """You are an experienced academic advisor with expertise in educational psychology, Arabic and Islamic studies (PhD) and student development.
Provide insightful, honest, encouraging, and practical academic performance analyses.
STRICT RULES:
- Plain text only. No markdown, no asterisks, no bold, no bullet points, no symbols.
- Write in full professional paragraphs only.
- Never start a line with *, **, #, or -.
- Reference actual subject names and scores in your analysis."""

    # --- Per-term individual reports ---
    for term in sorted_terms:
        data = terms_data[term]
        scores = data["scores"]
        total_subj = data["total_subjects"] or len(scores)
        avg = sum(scores) / total_subj if total_subj else 0
        highest = max(scores) if scores else 0
        lowest = min(scores) if scores else 0
        session = data["session"] or ""

        prompt = f"""Write a detailed academic performance report for {student_name or 'the student'} for {term} ({session}).

Performance Summary:
Average Score: {avg:.1f}%
Highest Score: {highest}%
Lowest Score: {lowest}%

Subject Scores:
{chr(10).join(data['subjects'])}

Cover the following in flowing paragraphs:
1. Overall performance and general academic standing for this term.
2. Subject strengths — subjects where the student scored 70% and above.
3. Areas needing improvement — subjects below 50%.
4. Two or three specific practical recommendations for weaker subjects.
5. A short encouraging closing sentence.

Do not use bullet points, markdown, asterisks, dashes, or bold text. Write everything in plain paragraphs."""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.6,
                top_p=0.9
            )
            term_report = response.choices[0].message.content.strip()
        except Exception as e:
            term_report = f"Unable to generate report for this term. Error: {str(e)}"

        full_report.append(
            f"{'=' * 50}\n"
            f"{term.upper()} - {session}\n"
            f"{'=' * 50}\n\n"
            f"{term_report}"
        )

    # --- Cross-term comparison (only if more than one term) ---
    if len(sorted_terms) > 1:
        comparison_lines = []
        for term in sorted_terms:
            data = terms_data[term]
            scores = data["scores"]
            total_subj = data["total_subjects"] or len(scores)
            avg = sum(scores) / total_subj if total_subj else 0
            comparison_lines.append(
                f"{term}: Average {avg:.1f}%, Highest {max(scores)}%, Lowest {min(scores)}%"
            )

        comparison_prompt = f"""Compare the academic performance of {student_name or 'the student'} across the following terms:

{chr(10).join(comparison_lines)}

Cover the following in flowing paragraphs:
1. Overall trend — is the student improving, declining, or consistent across terms?
2. Notable changes in specific subjects or areas between terms.
3. The overall academic trajectory and what it means for the student.
4. A strong motivating closing statement.

Do not use bullet points, markdown, asterisks, dashes, or bold text. Write everything in plain paragraphs."""

        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are an experienced academic advisor providing cross-term performance comparison. Plain text only, no markdown, no bold, no bullet points."},
                    {"role": "user", "content": comparison_prompt}
                ],
                max_tokens=500,
                temperature=0.6,
                top_p=0.9
            )
            comparison_report = response.choices[0].message.content.strip()
            full_report.append(
                f"{'=' * 50}\n"
                f"CROSS-TERM COMPARISON\n"
                f"{'=' * 50}\n\n"
                f"{comparison_report}"
            )
        except Exception as e:
            pass

    return "\n\n".join(full_report)