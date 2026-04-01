# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

After the basic app was working, four smart features were added to make scheduling more useful.

**Sorted time slots** — When a schedule is generated, each task is automatically given a start and end time (e.g. 08:00–08:30). Tasks are displayed in chronological order so the owner can follow the plan from top to bottom without any guesswork.

**Filter by pet or status** — Every task tracks which pet it belongs to and whether it is pending, done, or skipped. The owner can filter the task list to see only what still needs to be done, what has already been completed, or what was left out of today's plan.

**Recurring tasks** — A task can be set to repeat daily or weekly. Recurring tasks are given a small scheduling boost — when two tasks have the same priority, the recurring one is picked first. This keeps consistent routines (like feeding or a morning walk) from being bumped by one-off tasks.

**Automatic next occurrence** — When the owner marks a recurring task as done, the app immediately creates a fresh copy of that task for the next occurrence and sets its due date automatically (today + 1 day for daily, today + 7 days for weekly). The owner never has to re-enter a routine task manually.

**Conflict detection** — If two tasks end up overlapping in time (for example, when a task has a manually set start time that collides with another), the app flags it clearly in the schedule and shows exactly which tasks conflict and when.


## Testing Pawpal+

Tests live in `tests/test_pawpal.py` and use **pytest**. Run them from the project root:

```bash
pytest tests/test_pawpal.py -v
```

### What is tested

Five core scheduling behaviours are verified:

**1. Greedy scheduling respects available time** — `filter_by_time` selects tasks by priority until the owner's `available_minutes` budget is exhausted. Tests confirm that tasks exceeding remaining time are excluded and the total scheduled duration never exceeds the budget.

**2. Priority ordering** — High-priority tasks are always chosen over lower-priority ones when time is tight. A recurring task wins a tie-break against a non-recurring task at the same priority level.

**3. Conflict detection** — `detect_conflicts` flags pairs of tasks whose time windows overlap. Tests confirm that auto-assigned sequential times produce no conflicts, while manually set overlapping start times are caught correctly.

**4. `mark_task_done` and automatic next occurrence** — Marking a task done sets its status to `"done"`. If the task recurs, a fresh `"pending"` copy is appended with the correct `due_date` (today + 1 day for daily, today + 7 days for weekly), inheriting `pet_name`, `priority`, `duration_minutes`, and `recurrence`. Non-recurring tasks return `None` with no new task added.

**5. Filter by status and pet** — `filter_by_status` returns only tasks matching the requested status. `filter_by_pet` returns only tasks whose `pet_name` matches. Tasks with status `"done"` before `generate_plan` is called are never scheduled or re-skipped.