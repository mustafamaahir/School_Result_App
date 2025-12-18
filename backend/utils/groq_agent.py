# backend/utils/groq_agent.py

import os
from typing import List, Union, Dict, Any
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Validate API key before initializing client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is missing. Set it in your .env file or environment variables."
    )

client = Groq(api_key=GROQ_API_KEY)


def _build_prompt(results: List[Union[Dict[str, Any], Any]]) -> str:
    """Build a comprehensive prompt for academic performance analysis."""
    if not results:
        return ""
    
    student_name = None
    subject_scores = []
    terms_sessions = set()

    for r in results:
        name = getattr(r, "name", None) or (r.get("name") if isinstance(r, dict) else None)
        subject = getattr(r, "subject", None) or (r.get("subject") if isinstance(r, dict) else None)
        percentage = getattr(r, "percentage", None) or (r.get("percentage") if isinstance(r, dict) else None)
        term = getattr(r, "term", None) or (r.get("term") if isinstance(r, dict) else None)
        session = getattr(r, "session", None) or (r.get("session") if isinstance(r, dict) else None)

        if not student_name and name:
            student_name = name

        if subject and percentage is not None:
            subject_scores.append(f"• {subject}: {percentage}%")
        
        if term and session:
            terms_sessions.add(f"{term} ({session})")

    # Extract percentages
    percentages = [
    getattr(r, "percentage", None) or (r.get("percentage") if isinstance(r, dict) else None)
    for r in results
]
    percentages = [p for p in percentages if p is not None]

    # Extract total_subjects from payload (single source of truth)
    total_subjects = None
    for r in results:
        total_subjects = getattr(r, "total_subjects", None) or (
            r.get("total_subjects") if isinstance(r, dict) else None
    )
        if total_subjects:
            break

    subjects_taken = len(percentages)
    total_score = sum(percentages)

    # GUARANTEED correct average
    avg_score = (
        total_score / total_subjects
        if total_subjects and total_subjects > 0
        else 0
)

    highest = max(percentages) if percentages else 0
    lowest = min(percentages) if percentages else 0
    
    # Build comprehensive prompt
    prompt = f"""Analyze the following academic performance for {student_name or 'the student'}:

    ACADEMIC PERIOD:
    {', '.join(sorted(terms_sessions)) if terms_sessions else 'Current Session'}

    PERFORMANCE SUMMARY:
    - Subjects Taken: {subjects_taken}
    - Total Subjects: {total_subjects}
    - Average Score: {avg_score:.1f}%
    - Highest Score: {highest}%
    - Lowest Score: {lowest}%
    DETAILED SUBJECT SCORES:
    {chr(10).join(subject_scores)}

    REQUIRED ANALYSIS:
    Provide a comprehensive academic performance report covering:

    1. OVERALL PERFORMANCE: Assess the student's general academic standing based on the average score and score distribution.

    2. SUBJECT STRENGTHS: Identify top-performing subjects (scores ≥70%) and explain what these reveal about the student's aptitudes.

    3. AREAS FOR IMPROVEMENT: Highlight subjects needing attention (scores <50%) and discuss potential underlying challenges.

    4. PERFORMANCE PATTERNS: Note any significant gaps between highest and lowest scores, consistency across subjects, or concerning trends.

    5. ACTIONABLE RECOMMENDATIONS: Provide 3-4 specific, practical strategies for improvement including:
   - Study techniques for weaker subjects
   - Time management advice
   - Resource suggestions (tutoring, practice materials)
   - Motivational approach

    6. ENCOURAGEMENT: End with a motivating statement that acknowledges efforts and builds confidence.

    Write in a professional yet encouraging tone. Use complete paragraphs, not bullet points. Be specific and reference actual scores where relevant."""
    
    return prompt


def generate_student_report(results: List[Union[Dict[str, Any], Any]]) -> str:
    """
    Generate a comprehensive student academic performance analysis using Groq LLM.
    
    Args:
        results: List of student result entries (dicts or objects)
        
    Returns:
        Generated comprehensive analysis text or error message
    """
    if not results:
        return "No results available to generate a report."

    prompt = _build_prompt(results)
    if not prompt:
        return "Unable to build prompt from provided results."

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # ✅ Updated to latest model
            messages=[
                {
                    "role": "system",
                    "content": """You are an experienced academic advisor with expertise in educational psychology, Arabic and Islamic studies (PhD) and student development. 
Your role is to provide insightful, evidence-based academic performance analyses that are:
- Objective and data-driven
- Encouraging yet honest
- Actionable and practical
- Tailored to individual student needs
- Written in clear, professional language

Focus on helping students understand their performance and providing concrete steps for improvement."""
                },
                {"role": "user", "content": prompt}
            ],
            max_tokens=1200,  # ✅ Increased for comprehensive analysis
            temperature=0.6,   # ✅ Balanced creativity and consistency
            top_p=0.9
        )
        
        content = response.choices[0].message.content.strip()
        return content if content else "The model returned an empty response."
        
    except Exception as e:
        error_msg = str(e)
        # Provide user-friendly error messages
        if "model_decommissioned" in error_msg:
            return "The analysis service is currently being updated. Please try again shortly."
        elif "rate_limit" in error_msg.lower():
            return "Analysis service is experiencing high demand. Please try again in a few moments."
        elif "api_key" in error_msg.lower():
            return "Analysis service configuration error. Please contact your administrator."
        else:
            return f"Unable to generate performance analysis at this time. Please try again later."