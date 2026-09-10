from fastapi import APIRouter, HTTPException, status

from app.ai.scheduler import generate_schedule
from app.core.config import settings
from app.db.database import db_cursor, execute, fetch_all, fetch_one, to_jsonable
from app.schemas.requests import (
    AvailabilityCreate,
    SessionStatusUpdate,
    SubjectCreate,
    TaskCreate,
    TaskStatusUpdate,
)

router = APIRouter()


def not_found(message: str):
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)


@router.get("/subjects")
def get_subjects():
    return to_jsonable(fetch_all("SELECT * FROM subjects ORDER BY name"))


@router.post("/subjects", status_code=status.HTTP_201_CREATED)
def create_subject(payload: SubjectCreate):
    subject_id = execute(
        "INSERT INTO subjects(name, priority, difficulty) VALUES (%s, %s, %s)",
        (payload.name, payload.priority, payload.difficulty),
    )
    return to_jsonable(fetch_one("SELECT * FROM subjects WHERE id=%s", (subject_id,)))


@router.get("/tasks")
def get_tasks():
    rows = fetch_all(
        """
        SELECT t.*, s.name AS subject_name
        FROM study_tasks t
        JOIN subjects s ON s.id = t.subject_id
        ORDER BY t.deadline, t.priority DESC
        """
    )
    return to_jsonable(rows)


@router.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    if not fetch_one("SELECT id FROM subjects WHERE id=%s", (payload.subject_id,)):
        not_found("Môn học không tồn tại")

    task_id = execute(
        """
        INSERT INTO study_tasks(
            subject_id, title, estimated_hours, deadline,
            priority, difficulty, notes, resource_link
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            payload.subject_id,
            payload.title,
            payload.estimated_hours,
            payload.deadline,
            payload.priority,
            payload.difficulty,
            payload.notes.strip() if payload.notes and payload.notes.strip() else None,
            str(payload.resource_link) if payload.resource_link else None,
        ),
    )
    row = fetch_one(
        """
        SELECT t.*, s.name AS subject_name
        FROM study_tasks t JOIN subjects s ON s.id=t.subject_id
        WHERE t.id=%s
        """,
        (task_id,),
    )
    return to_jsonable(row)


@router.patch("/tasks/{task_id}/status")
def update_task_status(task_id: int, payload: TaskStatusUpdate):
    if not fetch_one("SELECT id FROM study_tasks WHERE id=%s", (task_id,)):
        not_found("Công việc không tồn tại")
    execute("UPDATE study_tasks SET status=%s WHERE id=%s", (payload.status, task_id))
    return {"ok": True}


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if not fetch_one("SELECT id FROM study_tasks WHERE id=%s", (task_id,)):
        not_found("Công việc không tồn tại")
    with db_cursor() as (_, cursor):
        cursor.execute("DELETE FROM study_sessions WHERE task_id=%s", (task_id,))
        cursor.execute("DELETE FROM study_tasks WHERE id=%s", (task_id,))
    return {"ok": True}


@router.get("/availability")
def get_availability():
    return to_jsonable(fetch_all("SELECT * FROM availability ORDER BY study_date, start_time"))


@router.post("/availability", status_code=status.HTTP_201_CREATED)
def create_availability(payload: AvailabilityCreate):
    overlap = fetch_one(
        """
        SELECT id FROM availability
        WHERE study_date=%s
          AND NOT (end_time <= %s OR start_time >= %s)
        LIMIT 1
        """,
        (payload.study_date, payload.start_time, payload.end_time),
    )
    if overlap:
        raise HTTPException(status_code=400, detail="Khoảng thời gian rảnh bị trùng với khoảng đã có")

    availability_id = execute(
        "INSERT INTO availability(study_date, start_time, end_time) VALUES (%s, %s, %s)",
        (payload.study_date, payload.start_time, payload.end_time),
    )
    return to_jsonable(fetch_one("SELECT * FROM availability WHERE id=%s", (availability_id,)))


@router.delete("/availability/{availability_id}")
def delete_availability(availability_id: int):
    if not fetch_one("SELECT id FROM availability WHERE id=%s", (availability_id,)):
        not_found("Khoảng thời gian rảnh không tồn tại")
    execute("DELETE FROM availability WHERE id=%s", (availability_id,))
    return {"ok": True}


@router.post("/schedule/generate")
def generate_ai_schedule():
    task_rows = fetch_all(
        """
        SELECT t.*, s.name AS subject_name,
               COALESCE(SUM(CASE WHEN ss.status = 'completed' THEN ss.duration_hours ELSE 0 END), 0) AS completed_hours
        FROM study_tasks t
        JOIN subjects s ON s.id=t.subject_id
        LEFT JOIN study_sessions ss ON ss.task_id=t.id
        WHERE t.status <> 'completed'
        GROUP BY t.id, s.name
        ORDER BY t.deadline
        """
    )

    # Khi lập lại lịch, chỉ xếp phần thời lượng còn thiếu của từng Task.
    # Nhờ đó các phiên đã hoàn thành không bị lập lịch lại từ đầu.
    tasks = []
    for row in task_rows:
        remaining = float(row["estimated_hours"]) - float(row.get("completed_hours") or 0)
        if remaining <= 0:
            continue
        task = dict(row)
        task["estimated_hours"] = remaining
        tasks.append(task)

    availability = fetch_all("SELECT * FROM availability ORDER BY study_date, start_time")

    if not tasks:
        raise HTTPException(status_code=400, detail="Không còn thời lượng Task nào cần lập lịch")
    if not availability:
        raise HTTPException(status_code=400, detail="Chưa khai báo thời gian rảnh")

    result = generate_schedule(tasks, availability, settings.scheduler_config())
    if not result["sessions"]:
        raise HTTPException(
            status_code=422,
            detail="Không thể tạo phiên học hợp lệ. Hãy kiểm tra deadline và thời gian rảnh.",
        )

    with db_cursor() as (_, cursor):
        cursor.execute("DELETE FROM study_sessions WHERE status <> 'completed'")
        for session in result["sessions"]:
            cursor.execute(
                """
                INSERT INTO study_sessions(
                    task_id, session_date, start_time, end_time,
                    duration_hours, status, fitness_score
                ) VALUES (%s, %s, %s, %s, %s, 'planned', %s)
                """,
                (
                    session["task_id"],
                    session["date"],
                    session["start"].time(),
                    session["end"].time(),
                    session["duration_hours"],
                    result["fitness"],
                ),
            )

    saved = fetch_all(
        """
        SELECT ss.*, t.title AS task_title, t.notes, t.resource_link,
               t.deadline, t.priority, t.difficulty, s.name AS subject_name
        FROM study_sessions ss
        JOIN study_tasks t ON t.id=ss.task_id
        JOIN subjects s ON s.id=t.subject_id
        ORDER BY ss.session_date, ss.start_time
        """
    )

    return to_jsonable({
        "message": "Đã tạo lịch học bằng Genetic Algorithm",
        "fitness": result["fitness"],
        "generations_run": result["ga"]["generations_run"],
        "history": result["ga"]["history"],
        "metrics": result["metrics"],
        "baseline": result["baseline"],
        "sessions": saved,
    })


@router.get("/schedule")
def get_schedule():
    rows = fetch_all(
        """
        SELECT ss.*, t.title AS task_title, t.notes, t.resource_link, t.deadline,
               t.priority, t.difficulty, s.name AS subject_name
        FROM study_sessions ss
        JOIN study_tasks t ON t.id=ss.task_id
        JOIN subjects s ON s.id=t.subject_id
        ORDER BY ss.session_date, ss.start_time
        """
    )
    return to_jsonable(rows)


@router.patch("/sessions/{session_id}/status")
def update_session_status(session_id: int, payload: SessionStatusUpdate):
    if not fetch_one("SELECT id FROM study_sessions WHERE id=%s", (session_id,)):
        not_found("Phiên học không tồn tại")
    execute("UPDATE study_sessions SET status=%s WHERE id=%s", (payload.status, session_id))
    return {"ok": True}


@router.get("/dashboard")
def dashboard():
    subjects = fetch_one("SELECT COUNT(*) AS count FROM subjects")["count"]
    tasks = fetch_one("SELECT COUNT(*) AS count FROM study_tasks")["count"]
    pending = fetch_one("SELECT COUNT(*) AS count FROM study_tasks WHERE status <> 'completed'")["count"]
    sessions = fetch_one("SELECT COUNT(*) AS count FROM study_sessions")["count"]
    return {
        "subjects": subjects,
        "tasks": tasks,
        "pending_tasks": pending,
        "sessions": sessions,
        "max_study_hours_per_day": settings.MAX_STUDY_HOURS_PER_DAY,
        "max_session_hours": settings.MAX_SESSION_HOURS,
        "slot_minutes": settings.SLOT_MINUTES,
    }
