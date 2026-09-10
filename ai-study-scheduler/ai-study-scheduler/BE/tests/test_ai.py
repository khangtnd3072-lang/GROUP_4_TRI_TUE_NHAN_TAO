from datetime import date, datetime, time

from app.ai.constraints import build_time_slots, repair_chromosome, validate_schedule
from app.ai.genetic_algorithm import GeneticScheduler
from app.ai.models import StudyTask
from app.ai.priority import calculate_priority_score
from app.ai.scheduler import chromosome_to_sessions


def make_task(task_id, title, hours, deadline, priority=3, difficulty=3):
    return StudyTask(
        id=task_id,
        subject_id=1,
        title=title,
        subject_name="AI",
        estimated_hours=hours,
        deadline=deadline,
        priority=priority,
        difficulty=difficulty,
    )


def availability(day, start="18:00", end="22:00"):
    return {
        "study_date": day,
        "start_time": time.fromisoformat(start),
        "end_time": time.fromisoformat(end),
    }


def test_priority_score_favors_urgent_high_priority_task():
    now = datetime(2026, 8, 26, 12, 0)
    urgent = make_task(1, "Urgent", 2, datetime(2026, 8, 27, 23, 59), 5, 5)
    later = make_task(2, "Later", 2, datetime(2026, 9, 20, 23, 59), 2, 2)
    assert calculate_priority_score(urgent, now) > calculate_priority_score(later, now)


def test_build_slots_uses_30_minute_resolution():
    slots = build_time_slots([availability(date(2026, 8, 27), "19:00", "21:00")], 30)
    assert len(slots) == 4
    assert slots[0].start.hour == 19
    assert slots[-1].end.hour == 21


def test_repair_enforces_three_hours_per_day():
    day = date(2026, 8, 27)
    slots = build_time_slots([availability(day, "18:00", "22:00")], 30)
    task = make_task(1, "Big task", 10, datetime(2026, 8, 30, 23, 59), 5, 5)
    genes = [1] * len(slots)
    repaired = repair_chromosome(
        genes, slots, {1: task}, {1: 1.0},
        slot_minutes=30,
        max_study_hours_per_day=3,
        max_session_hours=2,
    )
    assert sum(1 for gene in repaired if gene) <= 6
    assert not validate_schedule(repaired, slots, {1: task}, 30, 3)


def test_repair_removes_assignments_after_deadline():
    slots = build_time_slots([
        availability(date(2026, 8, 27), "19:00", "21:00"),
        availability(date(2026, 8, 29), "19:00", "21:00"),
    ], 30)
    task = make_task(1, "Deadline task", 4, datetime(2026, 8, 28, 23, 59), 5, 4)
    repaired = repair_chromosome([1] * len(slots), slots, {1: task}, {1: 1.0})
    for index, gene in enumerate(repaired):
        if gene:
            assert slots[index].end <= task.deadline


def test_genetic_algorithm_returns_valid_schedule_and_sessions_under_two_hours():
    tasks = [
        make_task(1, "GA", 2, datetime(2026, 8, 29, 23, 59), 5, 5),
        make_task(2, "Web", 1.5, datetime(2026, 8, 30, 23, 59), 3, 3),
    ]
    slots = build_time_slots([
        availability(date(2026, 8, 27), "18:00", "22:00"),
        availability(date(2026, 8, 28), "18:00", "22:00"),
    ], 30)
    scheduler = GeneticScheduler(
        tasks, slots,
        population_size=30,
        generations=50,
        random_seed=7,
        max_study_hours_per_day=3,
        max_session_hours=2,
    )
    chromosome, fitness, _ = scheduler.run()
    assert fitness > 0
    assert not validate_schedule(chromosome, slots, scheduler.tasks_by_id, 30, 3)

    sessions = chromosome_to_sessions(chromosome, slots, scheduler.tasks_by_id)
    assert sessions
    assert all(session["duration_hours"] <= 2 for session in sessions)
