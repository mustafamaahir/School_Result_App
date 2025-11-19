# backend/routers/results.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from database import get_db
import models
import statistics
import re
from utils.groq_agent import generate_student_report

router = APIRouter(prefix="/results", tags=["Results"])

@router.post("/upload")
async def upload_results(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload CSV/XLSX of results.
    Deletes results from previous sessions before inserting new session.
    """
    try:
        contents = await file.read()
        filename = file.filename.lower()
        buf = BytesIO(contents)

        # --- Extract term and session from filename ---
        term_match = re.search(r"(first|second|third)[_\s-]*term", filename, re.IGNORECASE)
        session_match = re.search(r"(\d{4})[_\s-]*(\d{4})", filename)

        term = term_match.group(1).capitalize() + " Term" if term_match else "Unknown Term"
        session = f"{session_match.group(1)}/{session_match.group(2)}" if session_match else "Unknown Session"

        # --- Load file content ---
        if filename.endswith(".csv"):
            df = pd.read_csv(buf)
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(buf)
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel (.xlsx/.xls)")

        # --- Check for required columns ---
        required_cols = {"Student Name", "Class", "Subject", "Percentage"}
        missing = required_cols - set(df.columns)
        if missing:
            raise HTTPException(status_code=400, detail=f"Missing columns: {', '.join(missing)}")

        # --- Delete old session before adding new session results ---
        if session != "Unknown Session":
            db.query(models.StudentResult).filter(models.StudentResult.session != session).delete()
            db.commit()

        records_added = 0
        mismatched_students = []
        teacher_id = None

        # --- Handle term ---
        if term_match:
            term_text = term_match.group(1).lower()
            term_map = {"1st": "First Term", "first": "First Term",
                        "2nd": "Second Term", "second": "Second Term",
                        "3rd": "Third Term", "third": "Third Term"}
            term = term_map.get(term_text, "Unknown Term")
        else:
            term = "Unknown Term"

        # --- Handle session ---
        if session_match:
            yr1, yr2 = session_match.groups()
            if len(yr2) == 2:
                yr2 = "20" + yr2
            session = f"{yr1}/{yr2}"
        else:
            session = "Unknown Session"

        # --- Insert results into database ---
        for _, row in df.iterrows():
            try:
                name = str(row["Student Name"]).strip()
                student_class = str(row["Class"]).strip()
                subject = str(row["Subject"]).strip()
                percentage = float(row["Percentage"])
            except Exception:
                continue

            user = (
                db.query(models.User)
                .filter(
                    (models.User.username.ilike(name)) |
                    (models.User.full_name.ilike(name))
                )
                .first()
            )

            student_id = user.id if user else None
            if not user:
                mismatched_students.append(name)

            new_result = models.StudentResult(
                name=name,
                student_class=student_class,
                subject=subject,
                percentage=percentage,
                student_id=student_id,
                teacher_id=teacher_id,
                term=term,
                session=session,
            )

            db.add(new_result)
            records_added += 1

        db.commit()
        db.close()

        msg = f"{records_added} results uploaded successfully for {term} ({session})."
        if mismatched_students:
            msg += f" {len(mismatched_students)} names not matched: {', '.join(mismatched_students[:5])}..."

        return {"message": msg, "term": term, "session": session, "records_added": records_added}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/myResults")
def get_student_result(username: str = None, db: Session = Depends(get_db)):
    """
    Returns results for a student by username.
    Includes all terms, min/max/median per subject per term.
    """
    if not username:
        raise HTTPException(status_code=400, detail="username query parameter is required")

    user = db.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch all results for this student
    results = db.query(models.StudentResult).filter(models.StudentResult.student_id == user.id).all()

    # Name fallback
    if not results:
        results = db.query(models.StudentResult).filter(
            models.StudentResult.name.ilike(f"%{user.username}%")
        ).all()
        if not results and user.full_name:
            results = db.query(models.StudentResult).filter(
                models.StudentResult.name.ilike(f"%{user.full_name}%")
            ).all()
        for r in results:
            if r.student_id is None:
                r.student_id = user.id
        db.commit()

    if not results:
        return {"results": [], "academic_analysis": None}

    # Group results per term for position
    term_positions = {}
    results_data = []

    # Determine latest term for default selection
    term_order = {"First Term": 1, "Second Term": 2, "Third Term": 3}
    available_terms = list(set([r.term for r in results]))
    latest_term = max(available_terms, key=lambda t: term_order.get(t, 0))

    for term in available_terms:
        # all student results in this term
        term_results = [r for r in results if r.term == term]

        if not term_results:
            continue

        # Compute ranking
        student_class = term_results[0].student_class

        class_students = (
            db.query(models.StudentResult.student_id)
            .filter(models.StudentResult.student_class == student_class,
                    models.StudentResult.term == term)
            .distinct()
            .all()
        )

        class_average_map = {}
        for (sid,) in class_students:
            scores = db.query(models.StudentResult).filter(
                models.StudentResult.student_id == sid,
                models.StudentResult.student_class == student_class,
                models.StudentResult.term == term
            ).all()
            if scores:
                avg = sum([s.percentage for s in scores]) / len(scores)
                class_average_map[sid] = avg

        sorted_avgs = sorted(class_average_map.values(), reverse=True)
        student_avg = sum([r.percentage for r in term_results]) / len(term_results)
        try:
            position = sorted_avgs.index(student_avg) + 1
        except ValueError:
            position = None

        def ordinal(n):
            return "%d%s" % (
                n,
                "tsnrhtdd"[(n // 10 % 10 != 1) * (n % 10 < 4) * n % 10::4]
            ) if n else ""

        term_positions[term] = {
            "position": position,
            "position_label": ordinal(position),
            "average_score": student_avg
        }

        # Class subject stats
        subjects_in_class = db.query(models.StudentResult.subject).filter(
            models.StudentResult.student_class == student_class,
            models.StudentResult.term == term
        ).distinct().all()

        class_subject_stats = {}
        for (subject,) in subjects_in_class:
            subject_scores = [
                r.percentage
                for r in db.query(models.StudentResult)
                .filter(models.StudentResult.student_class == student_class,
                        models.StudentResult.subject == subject,
                        models.StudentResult.term == term)
                .all()
            ]
            if subject_scores:
                class_subject_stats[subject] = {
                    "min": min(subject_scores),
                    "max": max(subject_scores),
                    "median": statistics.median(subject_scores)
                }

        for r in term_results:
            results_data.append({
                "name": r.name,
                "student_class": r.student_class,
                "subject": r.subject,
                "percentage": r.percentage,
                "term": r.term,
                "session": r.session,
                "min_score_in_class": class_subject_stats.get(r.subject, {}).get("min", 0),
                "max_score_in_class": class_subject_stats.get(r.subject, {}).get("max", 0),
                "median_score_in_class": class_subject_stats.get(r.subject, {}).get("median", 0)
            })

    # Academic analysis (latest term)
    academic_analysis = None
    try:
        latest_data = [
            r for r in results_data if r["term"] == latest_term
        ]
        academic_analysis = generate_student_report(latest_data)
    except:
        academic_analysis = None

    return {
        "results": results_data,
        "academic_analysis": academic_analysis,
        "student_name": user.full_name or user.username,
        "term_positions": term_positions,
        "latest_term": latest_term
    }


@router.get("/all")
def get_all_results(db: Session = Depends(get_db)):
    """Returns all uploaded results for admin analytics."""
    results = db.query(models.StudentResult).all()
    if not results:
        raise HTTPException(status_code=404, detail="No results found")

    return [
        {
            "id": r.id,
            "name": r.name,
            "student_class": r.student_class,
            "subject": r.subject,
            "percentage": r.percentage,
            "term": r.term,
            "session": r.session,
        }
        for r in results
    ]


@router.get("/class/{class_name}")
def get_class_results(class_name: str, db: Session = Depends(get_db)):
    results = db.query(models.StudentResult).filter(models.StudentResult.student_class == class_name).all()
    if not results:
        return []

    out = []
    for r in results:
        out.append({
            "id": r.id,
            "name": r.name,
            "student_class": r.student_class,
            "subject": r.subject,
            "percentage": r.percentage
        })
    return out