# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

My initial design had five classes: `Owner`, `Pet`, `Task`, `Scheduler`, and `Plan`.

- **Owner** holds the pet owner's name, how much time they have available in a day, and any personal preferences. It is responsible for providing that information to the scheduler.
- **Pet** holds the pet's name and species, and knows which owner it belongs to.
- **Task** represents a single care activity (like a walk or feeding). It stores the task name, how long it takes, and its priority level. It can compare itself to another task to determine which is more important.
- **Scheduler** is the main logic class. It takes an owner and a pet, holds a list of tasks, and is responsible for filtering tasks that fit within the owner's available time, sorting them by priority, and producing a daily plan.
- **Plan** holds the final list of scheduled tasks and the reasoning behind each choice. It is responsible for displaying the schedule clearly and explaining why each task was included.

The `Scheduler` sits at the center of the design — it uses the `Owner` and `Pet` as context, works with a list of `Task` objects, and produces a `Plan` as its output.

**b. Design changes**

Yes, the design changed during implementation. The main change was removing `Plan` as a standalone class.

In the initial design, `Plan` was its own class that held the scheduled tasks, total duration, and explanations, and had methods to display and explain the schedule. However, since `Plan` was always created and returned by `Scheduler`, it made more sense to just store that information directly on the `Scheduler` itself. After calling `generate_plan()`, the scheduler holds the results and you can call `display_plan()` and `explain_plan()` on it directly.

This simplified the code — there was one fewer class to maintain, and the scheduler became the single place responsible for both building and presenting the plan.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:

1. **Time** — the owner's `available_minutes` is a hard budget. `filter_by_time` accumulates task durations in priority order and stops adding tasks the moment one would exceed the remaining time.
2. **Priority** — tasks are ranked high (3) > medium (2) > low (1). Higher-priority tasks are always evaluated first, so a low-priority task can never displace a high-priority one.
3. **Recurrence** — within the same priority tier, a recurring task ranks above a non-recurring one. This acts as a secondary sort key so daily and weekly routines (feeding, morning walk) are never bumped by one-off tasks at the same level.

Tasks that are already `"done"` are excluded entirely before scheduling begins, so they never consume budget or reappear in the plan.

Time and priority were the most important constraints because they map directly to the two things a busy owner cares about: what they have time for, and what genuinely cannot be skipped. Recurrence as a tiebreaker felt natural because consistent routines matter for a pet's wellbeing.

**b. Tradeoffs**

The scheduler uses a **greedy algorithm**: it picks tasks one at a time in priority order and commits to each choice immediately without looking ahead. This means it can miss combinations that would fit. For example, if the budget is 30 minutes and the tasks are a 30-minute high-priority walk and two 15-minute medium-priority tasks, the greedy approach schedules the walk and skips both medium tasks — even though the two medium tasks would also fill the budget and might collectively be more valuable.

This tradeoff is reasonable here because the input sizes are small (a daily task list for one pet) and the results are predictable and easy for the owner to understand. A dynamic-programming or exhaustive search approach would be more optimal but would also be harder to reason about and unnecessary at this scale.

---

## 3. AI Collaboration

**a. How you used AI**

I used AI tools at several stages of the project:

- **Design brainstorming** — I described the scenario and asked the AI to help identify what attributes and methods each class should have. This was useful for quickly generating a starting point for the UML, though I adjusted it considerably afterward.
- **Debugging** — When the recurring-task tie-break in `sort_by_priority` was not working as expected, I pasted the method and asked what was wrong. The AI spotted that I needed a compound sort key `(PRIORITY_RANK[t.priority], 1 if t.recurrence else 0)` rather than sorting by priority alone.
- **Writing tests** — I asked the AI to suggest edge cases for `mark_task_done` that I might have missed. It prompted me to add tests for unknown titles, weekly due-date calculation, and attribute inheritance on the new task.

The most helpful prompts were specific ones that included the actual code and a concrete description of what I expected versus what was happening. Vague prompts like "help me with scheduling" produced generic answers; targeted prompts like "this method should prefer recurring tasks at equal priority — here is the current code, what is wrong?" produced directly useful answers.

**b. Judgment and verification**

When I was designing the class structure, the AI consistently suggested keeping `Plan` as a standalone class with its own `display` and `explain` methods and returning it from `generate_plan`. I pushed back on this. I traced the data flow manually: `Scheduler` creates a `Plan`, the UI immediately calls methods on it, and `Plan` itself holds no state that `Scheduler` doesn't already have access to. There was no scenario where a `Plan` object lived independently of the `Scheduler` that produced it.

I verified my decision by sketching out what the calling code would look like in both designs. The version with a separate `Plan` required the UI to chain through two objects (`scheduler.generate_plan().display()`), while folding the results into `Scheduler` let the UI call `scheduler.generate_plan()` and then read `scheduler.scheduled_tasks`, `scheduler.conflicts`, and `scheduler.explanations` directly — which was cleaner and easier to test.

---

## 4. Testing and Verification

**a. What you tested**

The test suite covers five categories of behavior:

1. **Greedy time-budget enforcement** — verified that tasks exceeding the remaining budget are excluded and that `total_duration` never exceeds `available_minutes`. This is the core contract of the scheduler, so it had to be airtight.
2. **Priority and recurrence ordering** — confirmed that high-priority tasks beat low-priority ones when time is tight, and that a recurring task beats a non-recurring task at the same priority level. These tests protect the tie-breaking logic, which is easy to break accidentally when modifying the sort key.
3. **Chronological time-slot assignment** — checked that `sort_by_time` returns tasks in ascending start-time order and that sequential auto-assigned times chain correctly (each task's `start_time` equals the previous task's `end_time`).
4. **Conflict detection** — confirmed that auto-assigned sequential times produce zero conflicts, and that manually overlapping start times are caught and reported correctly.
5. **`mark_task_done` and next-occurrence generation** — tested that marking a task done flips its status, that recurring tasks produce a new `pending` copy with the correct `due_date` (daily → +1 day, weekly → +7 days) and inherited attributes, and that non-recurring tasks return `None` with no new task added. Also tested the unknown-title edge case.

These tests matter because the scheduler's value is entirely in its correctness — if it silently over-schedules, drops high-priority tasks, or creates malformed recurring tasks, the owner gets a plan they cannot trust.

**b. Confidence**

I am confident the scheduler handles all the behaviors covered by the tests correctly. The tests are end-to-end (they call `generate_plan` on a real `Scheduler` object and assert on the resulting state), so they catch integration problems rather than just unit-level ones.

Edge cases I would test next with more time:
- `available_minutes = 0` — the scheduler should produce an empty plan without crashing.
- A task whose duration exactly equals the remaining budget — should be included (the greedy condition is `<=`, not `<`), but worth confirming explicitly.
- Duplicate task titles — `add_task` does not deduplicate; the UI guards against it, but the core class does not. A test would clarify the intended contract.
- A very large task list (100+ tasks) — verify that performance remains acceptable and that priority ordering is stable.
- `mark_task_done` called on a task not in `scheduled_tasks` but present in `tasks` — currently it still marks it done; it is worth deciding whether that is the intended behavior.

---

## 5. Reflection

**a. What went well**

I am most satisfied with the `mark_task_done` and automatic next-occurrence feature. Getting the interaction right — marking the original as done, creating a fresh copy that inherits all the right attributes, and setting the correct `due_date` based on recurrence type — required careful coordination between `Task.next_occurrence` and `Scheduler.mark_task_done`. The fact that the test suite then confirmed every aspect of that behavior (status, due date, pet name, recurrence, priority, duration) gave me real confidence that the feature works as intended. It also felt like the most genuinely useful feature from the owner's perspective: they never have to re-enter a routine task.

**b. What you would improve**

If I had another iteration, I would replace the greedy scheduling algorithm with a proper solution to the 0/1 knapsack problem. The current greedy approach can miss task combinations that would make better use of available time. For a small daily task list the difference is minor, but it becomes more noticeable when the owner has many medium-priority tasks of varying lengths.

I would also add time-of-day preferences so the owner can specify a preferred window for each task (e.g., walks before 09:00, meds at 18:00). Right now the scheduler fills time starting at 08:00 with no concept of when during the day a task should happen.

**c. Key takeaway**

The most important thing I learned is that a design should be treated as a hypothesis, not a commitment. The initial UML was a useful starting point, but the decision to remove the `Plan` class only became clear once I started implementing and could see the actual data flow. Staying willing to revise the design mid-implementation led to simpler, more readable code — and the same applies when working with AI: the AI's first suggestion is a starting point to evaluate, not an answer to accept. The skill is in knowing what questions to ask to verify whether a suggestion actually fits your specific situation.
