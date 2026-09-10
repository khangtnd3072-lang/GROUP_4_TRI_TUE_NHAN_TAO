from collections import Counter, defaultdict
import random

from .constraints import repair_chromosome, required_slots, slot_is_valid_for_task
from .priority import calculate_priority_score


class GeneticScheduler:
    def __init__(
        self,
        tasks,
        slots,
        slot_minutes=30,
        max_study_hours_per_day=3,
        max_session_hours=2,
        population_size=80,
        generations=180,
        mutation_rate=0.06,
        crossover_rate=0.85,
        elite_size=6,
        random_seed=42,
    ):
        self.tasks = list(tasks)
        self.slots = list(slots)
        self.slot_minutes = slot_minutes
        self.max_study_hours_per_day = max_study_hours_per_day
        self.max_session_hours = max_session_hours
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.elite_size = min(elite_size, population_size)
        self.random = random.Random(random_seed)

        self.tasks_by_id = {task.id: task for task in self.tasks}
        self.priority_scores = {task.id: calculate_priority_score(task) for task in self.tasks}
        self.required = {task.id: required_slots(task, slot_minutes) for task in self.tasks}
        self.valid_tasks_by_slot = {
            slot.index: [task.id for task in self.tasks if slot_is_valid_for_task(slot, task)]
            for slot in self.slots
        }

    def repair(self, chromosome):
        return repair_chromosome(
            chromosome,
            self.slots,
            self.tasks_by_id,
            self.priority_scores,
            slot_minutes=self.slot_minutes,
            max_study_hours_per_day=self.max_study_hours_per_day,
            max_session_hours=self.max_session_hours,
        )

    def _greedy_seed(self):
        genes = [0] * len(self.slots)
        tasks = sorted(
            self.tasks,
            key=lambda task: (-self.priority_scores[task.id], task.deadline),
        )

        for task in tasks:
            remaining = self.required[task.id]
            for i, slot in enumerate(self.slots):
                if remaining <= 0:
                    break
                if genes[i] == 0 and slot_is_valid_for_task(slot, task):
                    trial = list(genes)
                    trial[i] = task.id
                    repaired = self.repair(trial)
                    if repaired[i] == task.id:
                        genes = repaired
                        remaining -= 1
        return self.repair(genes)

    def _random_individual(self):
        genes = [0] * len(self.slots)
        for slot in self.slots:
            candidates = self.valid_tasks_by_slot[slot.index]
            if not candidates or self.random.random() < 0.20:
                continue

            weights = [max(self.priority_scores[task_id], 0.05) for task_id in candidates]
            task_id = self.random.choices(candidates, weights=weights, k=1)[0]
            genes[slot.index] = task_id
        return self.repair(genes)

    def initial_population(self):
        population = [self._greedy_seed()]
        while len(population) < self.population_size:
            population.append(self._random_individual())
        return population

    def evaluate(self, chromosome):
        counts = Counter(task_id for task_id in chromosome if task_id)
        fitness = 0.0

        # Reward completion, especially for urgent/high-priority tasks.
        for task in self.tasks:
            allocated = counts[task.id]
            needed = self.required[task.id]
            ratio = min(allocated / needed, 1.0)
            score = self.priority_scores[task.id]

            fitness += ratio * (120.0 + 120.0 * score)
            if allocated >= needed:
                fitness += 45.0 + 55.0 * score
            else:
                missing = needed - allocated
                fitness -= missing * (5.0 + 8.0 * score)

        # Reward productive use of available capacity without forcing every slot full.
        fitness += sum(counts.values()) * 1.5

        # Penalize unnecessary fragmentation of the same task across many sessions.
        sessions_by_task = defaultdict(int)
        prev_task = 0
        prev_end = None
        for i, task_id in enumerate(chromosome):
            if not task_id:
                prev_task = 0
                prev_end = None
                continue
            slot = self.slots[i]
            if task_id != prev_task or prev_end != slot.start:
                sessions_by_task[task_id] += 1
            prev_task = task_id
            prev_end = slot.end

        for task_id, session_count in sessions_by_task.items():
            ideal_min_sessions = max(1, (self.required[task_id] + 3) // 4)
            if session_count > ideal_min_sessions:
                fitness -= (session_count - ideal_min_sessions) * 2.0

        return round(fitness, 4)

    def _tournament(self, population, k=4):
        candidates = self.random.sample(population, min(k, len(population)))
        return max(candidates, key=self.evaluate)

    def _crossover(self, parent_a, parent_b):
        if len(parent_a) < 2 or self.random.random() > self.crossover_rate:
            return list(parent_a), list(parent_b)
        point = self.random.randint(1, len(parent_a) - 1)
        child_a = parent_a[:point] + parent_b[point:]
        child_b = parent_b[:point] + parent_a[point:]
        return self.repair(child_a), self.repair(child_b)

    def _mutate(self, chromosome):
        genes = list(chromosome)
        for i, slot in enumerate(self.slots):
            if self.random.random() >= self.mutation_rate:
                continue
            candidates = self.valid_tasks_by_slot[slot.index]
            choices = [0] + candidates
            if candidates:
                weights = [0.15] + [max(self.priority_scores[t], 0.05) for t in candidates]
                genes[i] = self.random.choices(choices, weights=weights, k=1)[0]
            else:
                genes[i] = 0
        return self.repair(genes)

    def run(self):
        if not self.tasks or not self.slots:
            return [0] * len(self.slots), 0.0, {"generations_run": 0, "history": []}

        population = self.initial_population()
        history = []
        best = max(population, key=self.evaluate)
        best_score = self.evaluate(best)
        stagnant = 0
        generations_run = 0

        for generation in range(self.generations):
            generations_run = generation + 1
            ranked = sorted(population, key=self.evaluate, reverse=True)
            current_score = self.evaluate(ranked[0])
            history.append(current_score)

            if current_score > best_score:
                best = list(ranked[0])
                best_score = current_score
                stagnant = 0
            else:
                stagnant += 1

            if stagnant >= 30:
                break

            next_population = [list(item) for item in ranked[: self.elite_size]]
            while len(next_population) < self.population_size:
                parent_a = self._tournament(ranked)
                parent_b = self._tournament(ranked)
                child_a, child_b = self._crossover(parent_a, parent_b)
                next_population.append(self._mutate(child_a))
                if len(next_population) < self.population_size:
                    next_population.append(self._mutate(child_b))
            population = next_population

        return best, best_score, {
            "generations_run": generations_run,
            "history": history,
        }
