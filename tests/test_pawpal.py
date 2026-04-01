import sys
import os
import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Owner, Pet, Task, Scheduler


# ── Existing tests ────────────────────────────────────────────────────────────

def test_high_priority_tasks_scheduled_before_low():
    """High priority tasks should be chosen over low priority ones when time is tight."""
    owner = Owner(name="Jordan", available_minutes=30)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Grooming", duration_minutes=25, priority="low"))
    scheduler.add_task(Task("Morning walk", duration_minutes=30, priority="high"))
    scheduler.generate_plan()

    titles = [t.title for t in scheduler.scheduled_tasks]
    assert "Morning walk" in titles
    assert "Grooming" not in titles


def test_tasks_exceeding_available_time_are_skipped():
    """Tasks that push the total over available time should not be scheduled."""
    owner = Owner(name="Jordan", available_minutes=20)
    pet = Pet(name="Luna", species="cat", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Feeding", duration_minutes=10, priority="high"))
    scheduler.add_task(Task("Vet check-in", duration_minutes=60, priority="medium"))
    scheduler.generate_plan()

    titles = [t.title for t in scheduler.scheduled_tasks]
    assert "Feeding" in titles
    assert "Vet check-in" not in titles
    assert scheduler.total_duration <= owner.available_minutes


# ── Sort by time ──────────────────────────────────────────────────────────────

def test_sort_by_time_returns_tasks_in_chronological_order():
    """sort_by_time should return scheduled tasks ordered by start_time ascending."""
    owner = Owner(name="Jordan", available_minutes=90)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet, day_start_minutes=480)  # 08:00

    scheduler.add_task(Task("Feeding", duration_minutes=10, priority="high"))
    scheduler.add_task(Task("Walk", duration_minutes=30, priority="high"))
    scheduler.add_task(Task("Playtime", duration_minutes=20, priority="medium"))
    scheduler.generate_plan()

    sorted_tasks = scheduler.sort_by_time()
    start_times = [t.start_time for t in sorted_tasks]
    assert start_times == sorted(start_times), "Tasks not in chronological order"


def test_start_times_are_assigned_sequentially():
    """After generate_plan, each task's start_time should equal the previous task's end_time."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet, day_start_minutes=480)

    scheduler.add_task(Task("Feeding", duration_minutes=10, priority="high"))
    scheduler.add_task(Task("Walk", duration_minutes=30, priority="high"))
    scheduler.generate_plan()

    sorted_tasks = scheduler.sort_by_time()
    assert sorted_tasks[0].start_time == 480
    assert sorted_tasks[1].start_time == sorted_tasks[0].end_time


# ── Filter by pet / status ────────────────────────────────────────────────────

def test_filter_by_status_returns_matching_tasks():
    """filter_by_status should return only tasks with the requested status."""
    owner = Owner(name="Jordan", available_minutes=30)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Feeding", duration_minutes=10, priority="high"))
    scheduler.add_task(Task("Grooming", duration_minutes=25, priority="low"))
    scheduler.generate_plan()

    # After generate_plan, Grooming is skipped because time runs out
    skipped = scheduler.filter_by_status("skipped")
    assert any(t.title == "Grooming" for t in skipped)

    pending = scheduler.filter_by_status("pending")
    assert all(t.status == "pending" for t in pending)


def test_filter_by_pet_returns_tasks_for_that_pet():
    """filter_by_pet should return only tasks whose pet_name matches."""
    owner = Owner(name="Jordan", available_minutes=90)
    mochi = Pet(name="Mochi", species="dog", owner=owner)
    mochi_scheduler = Scheduler(owner=owner, pet=mochi)
    mochi_scheduler.add_task(Task("Walk", duration_minutes=30, priority="high"))
    mochi_scheduler.add_task(Task("Feeding", duration_minutes=10, priority="high", pet_name="Luna"))

    mochi_tasks = mochi_scheduler.filter_by_pet("Mochi")
    luna_tasks = mochi_scheduler.filter_by_pet("Luna")

    assert all(t.pet_name == "Mochi" for t in mochi_tasks)
    assert all(t.pet_name == "Luna" for t in luna_tasks)
    assert len(mochi_tasks) == 1
    assert len(luna_tasks) == 1


def test_done_tasks_are_excluded_from_schedule():
    """Tasks with status='done' should never be scheduled."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Already fed", duration_minutes=10, priority="high", status="done"))
    scheduler.add_task(Task("Walk", duration_minutes=30, priority="medium"))
    scheduler.generate_plan()

    titles = [t.title for t in scheduler.scheduled_tasks]
    assert "Already fed" not in titles
    assert "Walk" in titles


# ── Recurring tasks ───────────────────────────────────────────────────────────

def test_recurring_task_next_occurrence_daily():
    """next_occurrence for a daily task should return tomorrow's date."""
    task = Task("Feeding", duration_minutes=10, priority="high", recurrence="daily")
    today = datetime.date(2026, 4, 1)
    assert task.next_occurrence(today) == datetime.date(2026, 4, 2)


def test_recurring_task_next_occurrence_weekly():
    """next_occurrence for a weekly task should return the date 7 days later."""
    task = Task("Vet check", duration_minutes=60, priority="medium", recurrence="weekly")
    today = datetime.date(2026, 4, 1)
    assert task.next_occurrence(today) == datetime.date(2026, 4, 8)


def test_non_recurring_task_returns_none():
    task = Task("Walk", duration_minutes=20, priority="high")
    assert task.next_occurrence() is None


def test_recurring_tasks_sorted_before_non_recurring_at_same_priority():
    """A recurring high-priority task should be preferred over a non-recurring one when time is tight."""
    owner = Owner(name="Jordan", available_minutes=20)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("One-off walk", duration_minutes=20, priority="high"))
    scheduler.add_task(Task("Daily feeding", duration_minutes=20, priority="high", recurrence="daily"))
    scheduler.generate_plan()

    titles = [t.title for t in scheduler.scheduled_tasks]
    assert "Daily feeding" in titles
    assert "One-off walk" not in titles


def test_next_recurring_tasks_returns_only_recurring():
    """next_recurring_tasks should only include tasks that have a recurrence set."""
    owner = Owner(name="Jordan", available_minutes=90)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Walk", duration_minutes=30, priority="high", recurrence="daily"))
    scheduler.add_task(Task("Grooming", duration_minutes=20, priority="low"))
    scheduler.generate_plan()

    recurring = scheduler.next_recurring_tasks(datetime.date(2026, 4, 1))
    assert len(recurring) == 1
    task, next_date = recurring[0]
    assert task.title == "Walk"
    assert next_date == datetime.date(2026, 4, 2)


# ── Conflict detection ────────────────────────────────────────────────────────

def test_no_conflicts_with_sequential_auto_assigned_times():
    """Auto-assigned start times should never produce conflicts."""
    owner = Owner(name="Jordan", available_minutes=90)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Feeding", duration_minutes=10, priority="high"))
    scheduler.add_task(Task("Walk", duration_minutes=30, priority="high"))
    scheduler.add_task(Task("Playtime", duration_minutes=20, priority="medium"))
    scheduler.generate_plan()

    assert scheduler.conflicts == []


def test_conflict_detected_when_tasks_overlap():
    """Two tasks with manually overlapping time windows should be detected as a conflict."""
    owner = Owner(name="Jordan", available_minutes=90)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    # Manually set overlapping start times: both start at 08:00, one is 30 min, other 20 min
    t1 = Task("Walk", duration_minutes=30, priority="high", start_time=480)
    t2 = Task("Feeding", duration_minutes=20, priority="high", start_time=490)  # starts inside Walk
    scheduler.add_task(t1)
    scheduler.add_task(t2)
    scheduler.generate_plan()

    assert len(scheduler.conflicts) == 1
    conflict_titles = {t.title for pair in scheduler.conflicts for t in pair}
    assert "Walk" in conflict_titles
    assert "Feeding" in conflict_titles


# ── mark_task_done ────────────────────────────────────────────────────────────

def test_mark_done_sets_status_to_done():
    """mark_task_done should flip the task's status to 'done'."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Walk", duration_minutes=30, priority="high"))
    scheduler.generate_plan()
    scheduler.mark_task_done("Walk")

    walk = next(t for t in scheduler.tasks if t.title == "Walk")
    assert walk.status == "done"


def test_mark_done_recurring_appends_new_task():
    """Completing a recurring task should add a fresh pending copy to self.tasks."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Feeding", duration_minutes=10, priority="high", recurrence="daily"))
    scheduler.generate_plan()

    initial_count = len(scheduler.tasks)
    next_task = scheduler.mark_task_done("Feeding")

    assert next_task is not None
    assert len(scheduler.tasks) == initial_count + 1
    assert next_task.status == "pending"
    assert next_task.recurrence == "daily"
    assert next_task.title == "Feeding"


def test_mark_done_non_recurring_returns_none():
    """Completing a non-recurring task should return None and not add any new task."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Grooming", duration_minutes=20, priority="medium"))
    scheduler.generate_plan()

    initial_count = len(scheduler.tasks)
    result = scheduler.mark_task_done("Grooming")

    assert result is None
    assert len(scheduler.tasks) == initial_count


def test_mark_done_unknown_title_returns_none():
    """mark_task_done with an unknown title should return None without side effects."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Walk", duration_minutes=30, priority="high"))
    scheduler.generate_plan()

    result = scheduler.mark_task_done("NonExistent")
    assert result is None


def test_mark_done_daily_sets_due_date_to_tomorrow():
    """The auto-created next occurrence for a daily task should have due_date = today + 1."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Feeding", duration_minutes=10, priority="high", recurrence="daily"))
    scheduler.generate_plan()
    next_task = scheduler.mark_task_done("Feeding")

    assert next_task.due_date == datetime.date.today() + datetime.timedelta(days=1)


def test_mark_done_weekly_sets_due_date_to_next_week():
    """The auto-created next occurrence for a weekly task should have due_date = today + 7."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Vet check", duration_minutes=30, priority="medium", recurrence="weekly"))
    scheduler.generate_plan()
    next_task = scheduler.mark_task_done("Vet check")

    assert next_task.due_date == datetime.date.today() + datetime.timedelta(weeks=1)


def test_new_occurrence_preserves_pet_name_and_recurrence():
    """The auto-created next occurrence should inherit pet_name and recurrence from the original."""
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Luna", species="cat", owner=owner)
    scheduler = Scheduler(owner=owner, pet=pet)

    scheduler.add_task(Task("Feeding", duration_minutes=10, priority="high", recurrence="weekly"))
    scheduler.generate_plan()
    next_task = scheduler.mark_task_done("Feeding")

    assert next_task.pet_name == "Luna"
    assert next_task.recurrence == "weekly"
    assert next_task.priority == "high"
    assert next_task.duration_minutes == 10
    assert next_task.due_date == datetime.date.today() + datetime.timedelta(weeks=1)