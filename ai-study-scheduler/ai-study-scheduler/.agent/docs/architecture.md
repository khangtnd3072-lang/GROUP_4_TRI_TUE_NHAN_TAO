# Architecture

## Flow

```text
FE/index.html + FE/css + FE/js
        ↓ REST/JSON
Python FastAPI (BE/app/api/routes.py)
        ↓
Scheduling service (BE/app/ai/scheduler.py)
        ↓
Priority Scoring → Constraints → Genetic Algorithm
        ↓
MySQL/MariaDB (XAMPP)
```

## Boundaries

- `FE/`: presentation, form handling, REST calls, timeline rendering only.
- `BE/app/api/routes.py`: HTTP validation and persistence orchestration.
- `BE/app/ai/priority.py`: task priority score only.
- `BE/app/ai/constraints.py`: slot creation, repair and hard-constraint validation.
- `BE/app/ai/genetic_algorithm.py`: optimization loop and fitness.
- `BE/app/ai/baseline.py`: Earliest Deadline First comparison algorithm.
- `BE/app/ai/scheduler.py`: maps database rows to AI domain objects and chromosomes to Study Sessions.
- `BE/app/db/database.py`: MySQL access helpers.
- `BE/database/`: SQL schema and demo data.

The AI engine can be unit-tested without running the frontend or MySQL.
