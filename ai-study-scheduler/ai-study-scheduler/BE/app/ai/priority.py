from datetime import datetime


def calculate_priority_score(task, now=None):
    """Return a normalized priority score in [0, 1].

    The score combines deadline urgency, explicit priority, difficulty,
    and estimated workload. Deadline urgency receives the largest weight.
    """
    now = now or datetime.now()
    days_left = (task.deadline.date() - now.date()).days

    if days_left <= 0:
        urgency = 1.0
    else:
        # 1.0 today, 0.5 at 7 days, then decreases smoothly.
        urgency = 1.0 / (1.0 + days_left / 7.0)

    priority_norm = min(max(task.priority, 1), 5) / 5.0
    difficulty_norm = min(max(task.difficulty, 1), 5) / 5.0
    workload_norm = min(max(task.estimated_hours, 0.0) / 10.0, 1.0)

    score = (
        0.45 * urgency
        + 0.30 * priority_norm
        + 0.15 * difficulty_norm
        + 0.10 * workload_norm
    )
    return round(min(max(score, 0.0), 1.0), 4)
