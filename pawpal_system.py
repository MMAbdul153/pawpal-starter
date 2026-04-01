class Owner:
    def __init__(self, name: str, available_minutes: int, preferences: list = None):
        self.name = name
        self.available_minutes = available_minutes
        self.preferences = preferences if preferences is not None else []

    def add_preference(self, preference: str):
        pass

    def get_available_time(self) -> int:
        pass


class Pet:
    def __init__(self, name: str, species: str, owner: Owner):
        self.name = name
        self.species = species
        self.owner = owner

    def get_info(self) -> str:
        pass


class Task:
    def __init__(self, title: str, duration_minutes: int, priority: str):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority

    def is_higher_priority_than(self, other: "Task") -> bool:
        pass

    def __repr__(self) -> str:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet):
        self.owner = owner
        self.pet = pet
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        pass

    def generate_plan(self) -> "Plan":
        pass

    def filter_by_time(self) -> list[Task]:
        pass

    def sort_by_priority(self) -> list[Task]:
        pass


class Plan:
    def __init__(self, scheduled_tasks: list[Task], explanations: dict[str, str]):
        self.scheduled_tasks = scheduled_tasks
        self.total_duration = sum(t.duration_minutes for t in scheduled_tasks)
        self.explanations = explanations

    def display(self) -> str:
        pass

    def explain(self) -> str:
        pass
