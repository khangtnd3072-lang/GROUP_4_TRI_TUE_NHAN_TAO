# Data Model

## subjects

Represents a course. Stores default human-entered priority and difficulty values.

## study_tasks

A task belongs to one subject and contains:

- estimated hours;
- deadline;
- priority 1–5;
- difficulty 1–5;
- status;
- optional notes/resource link.

The current AI uses task-level priority and difficulty directly.

## availability

A concrete date with a start/end time range when the student is available.

## study_sessions

Generated schedule output. Each record connects one task to one date/time range and stores the fitness score of the generated schedule.

There is intentionally no user/account table in this version because the assignment demo is single-user.
