from .constraints import required_slots, slot_is_valid_for_task


def earliest_deadline_first(scheduler):
    """Simple baseline: schedule earliest deadlines first, then priority."""
    genes = [0] * len(scheduler.slots)
    ordered_tasks = sorted(
        scheduler.tasks,
        key=lambda task: (task.deadline, -task.priority, -task.difficulty),
    )

    for task in ordered_tasks:
        remaining = required_slots(task, scheduler.slot_minutes)
        for i, slot in enumerate(scheduler.slots):
            if remaining <= 0:
                break
            if genes[i] != 0 or not slot_is_valid_for_task(slot, task):
                continue
            trial = list(genes)
            trial[i] = task.id
            repaired = scheduler.repair(trial)
            if repaired[i] == task.id:
                genes = repaired
                remaining -= 1

    genes = scheduler.repair(genes)
    return genes, scheduler.evaluate(genes)
