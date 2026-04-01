PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: list = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences if preferences is not None else []

    def add_preference(self, preference: str):
        self.preferences.append(preference)

    def get_available_time(self) -> int:
        return self.available_minutes


class Pet:
    def __init__(self, name: str, species: str, owner: Owner):
        self.name = name
        self.species = species
        self.owner = owner

    def get_info(self) -> str:
        return f"{self.name} ({self.species}), owned by {self.owner.name}"


class Task:
    def __init__(self, title: str, duration_minutes: int, priority: str):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority

    def is_higher_priority_than(self, other: "Task") -> bool:
        return PRIORITY_RANK[self.priority] > PRIORITY_RANK[other.priority]

    def __repr__(self) -> str:
        return f"Task('{self.title}', {self.duration_minutes}min, {self.priority})"


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []

        # Populated after generate_plan() is called
        self.scheduled_tasks: list[Task] = []
        self.total_duration: int = 0
        self.explanations: dict[str, str] = {}

    def add_task(self, task: Task):
        self.tasks.append(task)

    def sort_by_priority(self) -> list[Task]:
        return sorted(self.tasks, key=lambda t: PRIORITY_RANK[t.priority], reverse=True)

    def filter_by_time(self) -> list[Task]:
        """Pick tasks greedily by priority until available time is used up."""
        available = self.owner.get_available_time()
        chosen = []
        for task in self.sort_by_priority():
            if task.duration_minutes <= available:
                chosen.append(task)
                available -= task.duration_minutes
        return chosen

    def generate_plan(self):
        """Run scheduling logic and store results on this object."""
        self.scheduled_tasks = self.filter_by_time()
        self.total_duration = sum(t.duration_minutes for t in self.scheduled_tasks)
        self.explanations = {}

        skipped = {t.title for t in self.tasks} - {t.title for t in self.scheduled_tasks}

        for task in self.scheduled_tasks:
            self.explanations[task.title] = (
                f"Included because it has {task.priority} priority "
                f"and fits within {self.owner.name}'s available time."
            )
        for title in skipped:
            self.explanations[title] = "Skipped — not enough time remaining after higher-priority tasks."

    def display_plan(self) -> str:
        if not self.scheduled_tasks:
            return "No tasks could be scheduled. Check available time or add tasks."

        lines = [f"Daily plan for {self.pet.name}:"]
        for i, task in enumerate(self.scheduled_tasks, start=1):
            lines.append(f"  {i}. {task.title} — {task.duration_minutes} min [{task.priority} priority]")
        lines.append(f"\nTotal time: {self.total_duration} min / {self.owner.get_available_time()} min available")
        return "\n".join(lines)

    def explain_plan(self) -> str:
        if not self.explanations:
            return "No plan generated yet. Call generate_plan() first."

        lines = ["Plan explanation:"]
        for title, reason in self.explanations.items():
            lines.append(f"  - {title}: {reason}")
        return "\n".join(lines)
