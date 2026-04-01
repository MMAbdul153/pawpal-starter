import datetime

PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}


def _fmt_time(minutes: int) -> str:
    h, m = divmod(minutes, 60)
    return f"{h:02d}:{m:02d}"


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
    def __init__(
        self,
        title: str,
        duration_minutes: int,
        priority: str,
        start_time: int | None = None,
        status: str = "pending",
        recurrence: str | None = None,
        pet_name: str = "",
        due_date: datetime.date | None = None,
    ):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority
        self.start_time = start_time  # minutes from midnight, e.g. 480 = 08:00
        self.status = status          # "pending", "done", "skipped"
        self.recurrence = recurrence  # None, "daily", "weekly"
        self.pet_name = pet_name
        self.due_date = due_date

    @property
    def end_time(self) -> int | None:
        if self.start_time is None:
            return None
        return self.start_time + self.duration_minutes

    def is_higher_priority_than(self, other: "Task") -> bool:
        return PRIORITY_RANK[self.priority] > PRIORITY_RANK[other.priority]

    def next_occurrence(self, from_date: datetime.date | None = None) -> datetime.date | None:
        """Return the next recurrence date, or None if non-recurring."""
        if self.recurrence is None:
            return None
        base = from_date or datetime.date.today()
        if self.recurrence == "daily":
            return base + datetime.timedelta(days=1)
        if self.recurrence == "weekly":
            return base + datetime.timedelta(weeks=1)
        return None

    def __repr__(self) -> str:
        return f"Task('{self.title}', {self.duration_minutes}min, {self.priority})"


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, day_start_minutes: int = 480):
        self.owner = owner
        self.pet = pet
        self.day_start_minutes = day_start_minutes  # default 08:00
        self.tasks: list[Task] = []
        self.scheduled_tasks: list[Task] = []
        self.total_duration: int = 0
        self.explanations: dict[str, str] = {}
        self.conflicts: list[tuple[Task, Task]] = []

    def add_task(self, task: Task):
        if not task.pet_name:
            task.pet_name = self.pet.name
        self.tasks.append(task)

    def sort_by_priority(self) -> list[Task]:
        """Sort by priority desc; recurring tasks rank above non-recurring within the same tier."""
        return sorted(
            self.tasks,
            key=lambda t: (PRIORITY_RANK[t.priority], 1 if t.recurrence else 0),
            reverse=True,
        )

    def sort_by_time(self) -> list[Task]:
        """Return scheduled tasks sorted by start_time ascending (None-last)."""
        return sorted(
            self.scheduled_tasks,
            key=lambda t: (t.start_time is None, t.start_time or 0),
        )

    def filter_by_status(self, status: str) -> list[Task]:
        """Return all tasks with the given status."""
        return [t for t in self.tasks if t.status == status]

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return all tasks associated with the given pet name."""
        return [t for t in self.tasks if t.pet_name == pet_name]

    def filter_by_time(self) -> list[Task]:
        """Pick tasks greedily by priority until available time is used up.
        Tasks with status 'done' or 'skipped' are excluded."""
        available = self.owner.get_available_time()
        chosen = []
        for task in self.sort_by_priority():
            if task.status in ("done", "skipped"):
                continue
            if task.duration_minutes <= available:
                chosen.append(task)
                available -= task.duration_minutes
        return chosen

    def _assign_start_times(self, tasks: list[Task]) -> None:
        """Assign sequential start_times to tasks that don't already have one."""
        cursor = self.day_start_minutes
        for task in tasks:
            if task.start_time is None:
                task.start_time = cursor
            cursor = max(cursor, task.start_time) + task.duration_minutes

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of scheduled tasks whose time windows overlap."""
        timed = [
            t for t in self.scheduled_tasks
            if t.start_time is not None and t.end_time is not None
        ]
        conflicts = []
        for i, a in enumerate(timed):
            for b in timed[i + 1:]:
                if a.start_time < b.end_time and b.start_time < a.end_time:
                    conflicts.append((a, b))
        return conflicts

    def generate_plan(self):
        """Run scheduling logic and store results on this object."""
        self.scheduled_tasks = self.filter_by_time()
        self._assign_start_times(self.scheduled_tasks)
        self.total_duration = sum(t.duration_minutes for t in self.scheduled_tasks)
        self.conflicts = self.detect_conflicts()
        self.explanations = {}

        scheduled_titles = {t.title for t in self.scheduled_tasks}
        skipped = [t for t in self.tasks if t.title not in scheduled_titles and t.status != "done"]

        for task in self.scheduled_tasks:
            recur_note = f" Recurs {task.recurrence}." if task.recurrence else ""
            self.explanations[task.title] = (
                f"Included — {task.priority} priority, fits available time.{recur_note}"
            )
        for task in skipped:
            task.status = "skipped"
            self.explanations[task.title] = "Skipped — not enough time after higher-priority tasks."

    def display_plan(self) -> str:
        if not self.scheduled_tasks:
            return "No tasks could be scheduled. Check available time or add tasks."

        lines = [f"Daily plan for {self.pet.name}:"]
        for i, task in enumerate(self.sort_by_time(), start=1):
            time_str = ""
            if task.start_time is not None and task.end_time is not None:
                time_str = f" [{_fmt_time(task.start_time)}–{_fmt_time(task.end_time)}]"
            recur_str = f" ↻{task.recurrence}" if task.recurrence else ""
            due_str = f" (due {task.due_date})" if task.due_date else ""
            lines.append(
                f"  {i}. {task.title}{time_str} — {task.duration_minutes} min "
                f"[{task.priority}]{recur_str}{due_str}"
            )
        lines.append(f"\nTotal: {self.total_duration} min / {self.owner.get_available_time()} min available")

        if self.conflicts:
            lines.append("\nConflicts detected:")
            for a, b in self.conflicts:
                lines.append(
                    f"  - '{a.title}' ({_fmt_time(a.start_time)}–{_fmt_time(a.end_time)}) "
                    f"overlaps '{b.title}' ({_fmt_time(b.start_time)}–{_fmt_time(b.end_time)})"
                )

        return "\n".join(lines)

    def explain_plan(self) -> str:
        if not self.explanations:
            return "No plan generated yet. Call generate_plan() first."
        lines = ["Plan explanation:"]
        for title, reason in self.explanations.items():
            lines.append(f"  - {title}: {reason}")
        return "\n".join(lines)

    def mark_task_done(self, title: str) -> "Task | None":
        """Mark a task as done by title.

        If the task is recurring, a fresh pending copy is appended to self.tasks
        for the next occurrence and returned. Returns None if the title is not found.
        """
        for task in self.tasks:
            if task.title == title:
                task.status = "done"
                if task.recurrence:
                    next_task = Task(
                        title=task.title,
                        duration_minutes=task.duration_minutes,
                        priority=task.priority,
                        recurrence=task.recurrence,
                        pet_name=task.pet_name,
                        due_date=task.next_occurrence(),
                    )
                    self.tasks.append(next_task)
                    return next_task
                return None
        return None

    def next_recurring_tasks(
        self, from_date: datetime.date | None = None
    ) -> list[tuple[Task, datetime.date]]:
        """Return (task, next_date) for every recurring task in the current schedule."""
        return [
            (t, t.next_occurrence(from_date))
            for t in self.scheduled_tasks
            if t.recurrence is not None
        ]
