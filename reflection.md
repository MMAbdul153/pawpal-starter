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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
