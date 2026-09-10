"""Run repeatable AI-vs-baseline experiments without MySQL.

The script writes experiments/results.csv using actual algorithm executions.
Use these outputs as evidence for the report; do not replace them with invented values.
"""

import csv
import sys
from datetime import date, datetime, time, timedelta
from pathlib import Path
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.ai.scheduler import generate_schedule

CONFIG = {
    "SLOT_MINUTES": 30,
    "MAX_STUDY_HOURS_PER_DAY": 3,
    "MAX_SESSION_HOURS": 2,
    "GA_POPULATION_SIZE": 80,
    "GA_GENERATIONS": 180,
    "GA_MUTATION_RATE": 0.06,
    "GA_CROSSOVER_RATE": 0.85,
    "GA_ELITE_SIZE": 6,
    "GA_RANDOM_SEED": 42,
}

BASE_DAY = date(2026, 9, 1)


def task(task_id, title, hours, due_days, priority, difficulty, subject_id=1, subject_name="AI"):
    return {
        "id": task_id,
        "subject_id": subject_id,
        "subject_name": subject_name,
        "title": title,
        "estimated_hours": hours,
        "deadline": datetime.combine(BASE_DAY + timedelta(days=due_days), time(23, 59)),
        "priority": priority,
        "difficulty": difficulty,
    }


def avail(day_offset, start="18:00", end="22:00"):
    return {
        "id": day_offset + 1,
        "study_date": BASE_DAY + timedelta(days=day_offset),
        "start_time": time.fromisoformat(start),
        "end_time": time.fromisoformat(end),
    }


SCENARIOS = [
    (
        "01_low_load",
        [task(1, "GA theory", 2, 3, 5, 5), task(2, "Web UI", 1.5, 4, 3, 2)],
        [avail(0), avail(1), avail(2)],
    ),
    (
        "02_tight_deadlines",
        [
            task(1, "AI report", 3, 1, 5, 5),
            task(2, "Database exercise", 2.5, 1, 4, 4, 2, "Database"),
            task(3, "Web demo", 2, 2, 4, 3, 3, "Web"),
        ],
        [avail(0), avail(1), avail(2)],
    ),
    (
        "03_limited_availability",
        [
            task(1, "AI coding", 5, 3, 5, 5),
            task(2, "DB review", 4, 4, 4, 4, 2, "Database"),
            task(3, "Web review", 3, 4, 3, 3, 3, "Web"),
        ],
        [avail(0, "19:00", "21:00"), avail(1, "19:00", "21:00"), avail(2, "19:00", "21:00")],
    ),
    (
        "04_priority_competition",
        [
            task(1, "Critical AI", 3, 3, 5, 5),
            task(2, "Critical DB", 3, 3, 5, 4, 2, "Database"),
            task(3, "Normal Web", 3, 3, 2, 2, 3, "Web"),
            task(4, "Optional reading", 2, 5, 1, 2),
        ],
        [avail(0), avail(1), avail(2)],
    ),
    (
        "05_larger_case",
        [
            task(1, "AI chapter 1", 2, 2, 5, 4),
            task(2, "AI chapter 2", 2.5, 4, 5, 5),
            task(3, "DB normalization", 2, 3, 4, 4, 2, "Database"),
            task(4, "SQL practice", 2.5, 5, 3, 3, 2, "Database"),
            task(5, "Web frontend", 2, 4, 4, 3, 3, "Web"),
            task(6, "Web backend", 3, 6, 4, 4, 3, "Web"),
            task(7, "Presentation", 1.5, 6, 5, 2),
        ],
        [avail(i) for i in range(7)],
    ),
]


def main():
    rows = []
    for name, tasks, availability in SCENARIOS:
        started = perf_counter()
        result = generate_schedule(tasks, availability, CONFIG)
        elapsed = perf_counter() - started
        rows.append({
            "scenario": name,
            "ga_fitness": result["fitness"],
            "edf_fitness": result["baseline"]["fitness"],
            "ga_full_schedule_rate": result["metrics"]["full_schedule_rate"],
            "edf_full_schedule_rate": result["baseline"]["metrics"]["full_schedule_rate"],
            "ga_completion_ratio": result["metrics"]["average_completion_ratio"],
            "edf_completion_ratio": result["baseline"]["metrics"]["average_completion_ratio"],
            "ga_allocated_hours": result["metrics"]["allocated_hours"],
            "edf_allocated_hours": result["baseline"]["metrics"]["allocated_hours"],
            "generations_run": result["ga"]["generations_run"],
            "execution_seconds": round(elapsed, 6),
        })

    output = Path(__file__).with_name("results.csv")
    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {output}")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
