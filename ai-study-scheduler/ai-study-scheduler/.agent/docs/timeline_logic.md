# AI Scheduling Logic

## 1. Priority Scoring

Each task receives a score in [0, 1]:

```text
0.45 * urgency
+ 0.30 * priority
+ 0.15 * difficulty
+ 0.10 * workload
```

Urgency is based on remaining days to the deadline. Priority and difficulty are normalized from the 1–5 input scale. Workload is capped after normalization.

## 2. Slot Representation

Availability windows are divided into 30-minute slots. One chromosome has exactly one gene per slot.

```text
0 = idle
N = schedule task ID N in this slot
```

## 3. Hard Constraints

`repair_chromosome()` guarantees:

- known task IDs only;
- no assignment after deadline;
- no task over-allocation;
- maximum six occupied 30-minute slots/day = 3 hours;
- maximum four continuous slots = 2 hours;
- a break slot when switching tasks inside contiguous availability.

## 4. Fitness

The fitness function rewards partial/full task scheduling, weighted by Priority Score. It also rewards productive slot use and penalizes unnecessary fragmentation.

Because hard violations are repaired rather than merely penalized, candidate schedules that survive evaluation are structurally valid under the configured hard constraints.

## 5. Genetic Operators

- Selection: tournament selection.
- Crossover: one-point crossover.
- Mutation: replace a gene with an allowed task or idle.
- Elitism: top individuals pass to the next generation unchanged.
- Early stopping: no improvement for 30 generations.
