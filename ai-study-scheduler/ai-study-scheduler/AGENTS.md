# 1. Project Overview

AI Study Scheduler is a single-user Artificial Intelligence course project. It creates study sessions from tasks, deadlines and availability using Priority Scoring, constraint repair and a Genetic Algorithm, then compares the result with an Earliest Deadline First baseline.

# 2. Tech Stack

- Frontend: HTML5, CSS3, vanilla JavaScript ES modules.
- Backend: Python + FastAPI 0.116.1.
- ASGI server: Uvicorn 0.35.0.
- Database: MySQL/MariaDB via XAMPP, using mysql-connector-python 9.4.0.
- Configuration: pydantic-settings 2.10.1 + `.env`.
- Tests: pytest 9.0.2.

# 3. Dev Commands

Backend setup:

```bat
cd BE
setup_backend.bat
```

Backend server:

```bat
cd BE
run_backend.bat
```

Frontend server:

```bat
cd FE
run_frontend.bat
```

Tests:

```bat
cd BE
.venv\Scripts\activate
pytest -q
```

There is no frontend build step and no npm dependency.

# 4. Core Logic Summary

- Availability is split into 30-minute slots.
- Priority Scoring combines deadline urgency, explicit priority, difficulty and workload.
- A chromosome maps each slot to a task ID or `0` for idle.
- Constraint repair enforces deadline, remaining workload, max 3 hours/day, max 2 continuous hours/session and a break when switching tasks in contiguous time.
- Genetic Algorithm uses tournament selection, one-point crossover, mutation, elitism and stagnation-based early stopping.
- Completed sessions are preserved during re-scheduling; only remaining task duration is scheduled again.
- `BE/app/ai/baseline.py` provides Earliest Deadline First for comparison.

# 5. Key Constraints

- Keep FE and BE separated; do not move scheduling logic into frontend JavaScript.
- Do not add authentication unless the assignment scope changes.
- Keep `SLOT_MINUTES=30` unless tests/docs are updated.
- Daily study allocation must not exceed 3 hours by default.
- A continuous session must not exceed 2 hours by default.
- Never schedule a task after its deadline.
- Do not allocate more than the remaining estimated duration of a task.
- Experimental metrics must come from actual executions; never invent report values.
- If fitness weights or hard constraints change, update tests and documentation.

# 6. Additional Documentation

- Architecture → `.agent/docs/architecture.md`
- AI scheduling logic → `.agent/docs/timeline_logic.md`
- Data model → `.agent/docs/data_model.md`
- Experiment design → `.agent/docs/experiments.md`
- Run guide → `HUONG_DAN_CHAY_CHUONG_TRINH.md`
- Report outline → `docs/report_outline.md`
