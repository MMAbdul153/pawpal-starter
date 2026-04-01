import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Owner, Pet, Task, Scheduler


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
