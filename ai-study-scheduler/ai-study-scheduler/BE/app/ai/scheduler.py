from collections import Counter
from datetime import datetime

from .baseline import earliest_deadline_first
from .constraints import build_time_slots, required_slots
from .genetic_algorithm import GeneticScheduler
from .models import StudyTask
from .priority import calculate_priority_score


def _as_datetime(value):
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value))


def rows_to_tasks(task_rows):
    return [
        StudyTask(
            id=int(row["id"]),
            subject_id=int(row["subject_id"]),
            title=row["title"],
            subject_name=row.get("subject_name", ""),
            estimated_hours=float(row["estimated_hours"]),
            deadline=_as_datetime(row["deadline"]),
            priority=int(row["priority"]),
            difficulty=int(row["difficulty"]),
        )
        for row in task_rows
    ]


def chromosome_to_sessions(chromosome, slots, tasks_by_id):
    sessions = []
    current = None

    for i, task_id in enumerate(chromosome):
        if not task_id:
            if current:
                sessions.append(current)
                current = None
            continue

        slot = slots[i]
        task = tasks_by_id[task_id]
        can_extend = (
            current
            and current["task_id"] == task_id
            and current["end"] == slot.start
        )

        if can_extend:
            current["end"] = slot.end
            current["duration_hours"] += (slot.end - slot.start).total_seconds() / 3600
        else:
            if current:
                sessions.append(current)
            current = {
                "task_id": task_id,
                "task_title": task.title,
                "subject_id": task.subject_id,
                "subject_name": task.subject_name,
                "date": slot.start.date(),
                "start": slot.start,
                "end": slot.end,
                "duration_hours": (slot.end - slot.start).total_seconds() / 3600,
            }

    if current:
        sessions.append(current)
    return sessions


def build_metrics(chromosome, scheduler):
    counts = Counter(task_id for task_id in chromosome if task_id)
    completed = 0
    completion_ratios = []
    task_details = []

    for task in scheduler.tasks:
        need = scheduler.required[task.id]
        allocated = counts[task.id]
        ratio = min(allocated / need, 1.0)
        completion_ratios.append(ratio)
        if allocated >= need:
            completed += 1
        task_details.append({
            "task_id": task.id,
            "task_title": task.title,
            "priority_score": calculate_priority_score(task),
            "required_hours": round(need * scheduler.slot_minutes / 60, 2),
            "allocated_hours": round(allocated * scheduler.slot_minutes / 60, 2),
            "completion_ratio": round(ratio, 4),
        })

    total_tasks = len(scheduler.tasks)
    return {
        "tasks_fully_scheduled": completed,
        "total_tasks": total_tasks,
        "full_schedule_rate": round(completed / total_tasks, 4) if total_tasks else 0,
        "average_completion_ratio": round(sum(completion_ratios) / total_tasks, 4) if total_tasks else 0,
        "allocated_hours": round(sum(counts.values()) * scheduler.slot_minutes / 60, 2),
        "task_details": task_details,
    }


def generate_schedule(task_rows, availability_rows, config):
    tasks = rows_to_tasks(task_rows)
    slots = build_time_slots(availability_rows, config["SLOT_MINUTES"])

    scheduler = GeneticScheduler(
        tasks=tasks,
        slots=slots,
        slot_minutes=config["SLOT_MINUTES"],
        max_study_hours_per_day=config["MAX_STUDY_HOURS_PER_DAY"],
        max_session_hours=config["MAX_SESSION_HOURS"],
        population_size=config["GA_POPULATION_SIZE"],
        generations=config["GA_GENERATIONS"],
        mutation_rate=config["GA_MUTATION_RATE"],
        crossover_rate=config["GA_CROSSOVER_RATE"],
        elite_size=config["GA_ELITE_SIZE"],
        random_seed=config["GA_RANDOM_SEED"],
    )

    best, fitness, ga_info = scheduler.run()
    baseline, baseline_fitness = earliest_deadline_first(scheduler)

    sessions = chromosome_to_sessions(best, slots, scheduler.tasks_by_id)
    ai_metrics = build_metrics(best, scheduler)
    baseline_metrics = build_metrics(baseline, scheduler)

    return {
        "sessions": sessions,
        "fitness": fitness,
        "ga": ga_info,
        "metrics": ai_metrics,
        "baseline": {
            "algorithm": "Earliest Deadline First",
            "fitness": baseline_fitness,
            "metrics": baseline_metrics,
        },
        "slot_count": len(slots),
    }
