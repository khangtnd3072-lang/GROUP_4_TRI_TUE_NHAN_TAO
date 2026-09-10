from collections import Counter, defaultdict
from datetime import datetime, timedelta, time
import math

from .models import TimeSlot


def _normalize_time(value):
    if isinstance(value, time):
        return value

    if isinstance(value, timedelta):
        total_seconds = int(value.total_seconds())

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return time(
            hour=hours,
            minute=minutes,
            second=seconds,
        )

    if isinstance(value, str):
        return time.fromisoformat(value)

    raise TypeError(f"Kiểu thời gian không được hỗ trợ: {type(value)}")


def build_time_slots(availability_rows, slot_minutes=30):
    """Expand availability windows into fixed-size chronological slots."""
    slots = []

    for row in availability_rows:
        study_date = row["study_date"]
        start_time = _normalize_time(row["start_time"])
        end_time = _normalize_time(row["end_time"])

        start = datetime.combine(study_date, start_time)
        end = datetime.combine(study_date, end_time)

        cursor = start

        while cursor + timedelta(minutes=slot_minutes) <= end:
            slots.append(
                TimeSlot(
                    index=-1,
                    start=cursor,
                    end=cursor + timedelta(minutes=slot_minutes)
                )
            )
            cursor += timedelta(minutes=slot_minutes)

    slots.sort(key=lambda slot: slot.start)

    return [
        TimeSlot(index=i, start=s.start, end=s.end)
        for i, s in enumerate(slots)
    ]

def required_slots(task, slot_minutes=30):
    return max(1, math.ceil(task.estimated_hours * 60 / slot_minutes))


def slot_is_valid_for_task(slot, task):
    return slot.end <= task.deadline


def repair_chromosome(
    chromosome,
    slots,
    tasks_by_id,
    priority_scores,
    slot_minutes=30,
    max_study_hours_per_day=3,
    max_session_hours=2,
):
    """Repair hard-constraint violations in a chromosome.

    Genes contain task ids or 0 for idle. Repair guarantees:
    - assignment only inside known availability slots;
    - no task is scheduled after its deadline;
    - no task is over-allocated;
    - daily study duration does not exceed the configured maximum;
    - a continuous study block is at most max_session_hours;
    - a 30-minute break is inserted when switching tasks inside contiguous slots.
    """
    genes = list(chromosome)

    # 1) Remove unknown tasks and assignments after deadline.
    for i, task_id in enumerate(genes):
        if not task_id:
            continue
        task = tasks_by_id.get(task_id)
        if task is None or not slot_is_valid_for_task(slots[i], task):
            genes[i] = 0

    # 2) Prevent over-allocation. Keep earlier study time and drop later excess.
    allowed = {task_id: required_slots(task, slot_minutes) for task_id, task in tasks_by_id.items()}
    indexes_by_task = defaultdict(list)
    for i, task_id in enumerate(genes):
        if task_id:
            indexes_by_task[task_id].append(i)
    for task_id, indexes in indexes_by_task.items():
        overflow = len(indexes) - allowed[task_id]
        if overflow > 0:
            for i in reversed(indexes[-overflow:]):
                genes[i] = 0

    # 3) Enforce max study slots per day.
    max_daily_slots = int(max_study_hours_per_day * 60 / slot_minutes)
    day_indexes = defaultdict(list)
    for i, slot in enumerate(slots):
        if genes[i]:
            day_indexes[slot.date_key].append(i)

    for indexes in day_indexes.values():
        if len(indexes) <= max_daily_slots:
            continue
        # Remove lowest-scored tasks first; for ties remove later slots first.
        ranked = sorted(
            indexes,
            key=lambda idx: (priority_scores.get(genes[idx], 0.0), -idx),
        )
        for idx in ranked[: len(indexes) - max_daily_slots]:
            genes[idx] = 0

    # 4) Session rules: max continuous block and break before switching task.
    max_consecutive_slots = int(max_session_hours * 60 / slot_minutes)
    previous_slot = None
    previous_task = 0
    consecutive = 0

    for i, slot in enumerate(slots):
        task_id = genes[i]
        contiguous = previous_slot is not None and slot.start == previous_slot.end

        if not contiguous or not task_id:
            previous_task = task_id
            consecutive = 1 if task_id else 0
            previous_slot = slot
            continue

        if not previous_task:
            previous_task = task_id
            consecutive = 1
            previous_slot = slot
            continue

        # A task switch requires at least one empty 30-minute slot as a break.
        if task_id != previous_task:
            genes[i] = 0
            previous_task = 0
            consecutive = 0
            previous_slot = slot
            continue

        if consecutive >= max_consecutive_slots:
            genes[i] = 0
            previous_task = 0
            consecutive = 0
            previous_slot = slot
            continue

        consecutive += 1
        previous_task = task_id
        previous_slot = slot

    return genes


def validate_schedule(chromosome, slots, tasks_by_id, slot_minutes=30, max_study_hours_per_day=3):
    """Return human-readable hard constraint violations for diagnostics/tests."""
    violations = []
    daily = Counter()
    task_counts = Counter()

    for i, task_id in enumerate(chromosome):
        if not task_id:
            continue
        task = tasks_by_id.get(task_id)
        if not task:
            violations.append(f"Slot {i}: unknown task {task_id}")
            continue
        if not slot_is_valid_for_task(slots[i], task):
            violations.append(f"Slot {i}: task {task_id} is after deadline")
        daily[slots[i].date_key] += 1
        task_counts[task_id] += 1

    max_daily_slots = int(max_study_hours_per_day * 60 / slot_minutes)
    for day, count in daily.items():
        if count > max_daily_slots:
            violations.append(f"{day}: exceeds daily maximum")

    for task_id, count in task_counts.items():
        if count > required_slots(tasks_by_id[task_id], slot_minutes):
            violations.append(f"Task {task_id}: over-allocated")

    return violations
