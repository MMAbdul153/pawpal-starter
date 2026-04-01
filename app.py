import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler, _fmt_time

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.markdown(
    "Welcome to **PawPal+** — a pet care planning assistant that builds a daily "
    "schedule for your pet based on task priority and your available time."
)

st.divider()

# ── Owner & Pet ──────────────────────────────────────────────────────────────
st.subheader("Owner & Pet Info")

col_a, col_b = st.columns(2)
with col_a:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input(
        "Your available time today (minutes)", min_value=10, max_value=480, value=90
    )
with col_b:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])

st.divider()

# ── Add tasks ─────────────────────────────────────────────────────────────────
st.subheader("Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5 = st.columns(2)
with col4:
    recurrence = st.selectbox("Recurrence", ["none", "daily", "weekly"])
with col5:
    task_status = st.selectbox("Status", ["pending", "done"])

if st.button("Add task"):
    if task_title.strip():
        existing_titles = [t.title for t in st.session_state.tasks]
        if task_title.strip() in existing_titles:
            st.warning(f"A task named '{task_title.strip()}' already exists.")
        else:
            st.session_state.tasks.append(
                Task(
                    task_title.strip(),
                    int(duration),
                    priority,
                    status=task_status,
                    recurrence=None if recurrence == "none" else recurrence,
                )
            )

# ── Task list ─────────────────────────────────────────────────────────────────
if st.session_state.tasks:

    # Filter + Sort controls
    ctrl_a, ctrl_b = st.columns(2)
    with ctrl_a:
        status_filter = st.selectbox(
            "Filter by status",
            ["all", "pending", "done", "skipped"],
            key="status_filter",
        )
    with ctrl_b:
        sort_by = st.selectbox(
            "Sort by",
            ["priority (high → low)", "duration (short → long)", "title (A → Z)"],
            key="sort_by",
        )

    # Apply filter
    _PRIORITY_RANK = {"low": 1, "medium": 2, "high": 3}
    display_tasks = (
        st.session_state.tasks
        if status_filter == "all"
        else [t for t in st.session_state.tasks if t.status == status_filter]
    )

    # Apply sort
    if sort_by == "priority (high → low)":
        display_tasks = sorted(
            display_tasks, key=lambda t: _PRIORITY_RANK[t.priority], reverse=True
        )
    elif sort_by == "duration (short → long)":
        display_tasks = sorted(display_tasks, key=lambda t: t.duration_minutes)
    else:
        display_tasks = sorted(display_tasks, key=lambda t: t.title.lower())

    if display_tasks:
        # Priority and status badges
        _PRIORITY_ICON = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}
        _STATUS_ICON = {"pending": "⏳ pending", "done": "✅ done", "skipped": "⏭️ skipped"}

        st.table(
            [
                {
                    "Title": t.title,
                    "Duration (min)": t.duration_minutes,
                    "Priority": _PRIORITY_ICON.get(t.priority, t.priority),
                    "Status": _STATUS_ICON.get(t.status, t.status),
                    "Recurrence": t.recurrence or "—",
                }
                for t in display_tasks
            ]
        )

        # Quick summary metrics
        pending_count = sum(1 for t in st.session_state.tasks if t.status == "pending")
        done_count = sum(1 for t in st.session_state.tasks if t.status == "done")
        total_min = sum(t.duration_minutes for t in st.session_state.tasks if t.status == "pending")

        m1, m2, m3 = st.columns(3)
        m1.metric("Pending tasks", pending_count)
        m2.metric("Completed tasks", done_count)
        m3.metric("Pending time (min)", total_min)

    else:
        st.info(f"No tasks with status '{status_filter}'.")

    if st.button("Clear tasks"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# ── Build schedule ────────────────────────────────────────────────────────────
st.subheader("Build Schedule")

if st.button("Generate schedule"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        owner = Owner(name=owner_name, available_minutes=int(available_minutes))
        pet = Pet(name=pet_name, species=species, owner=owner)
        scheduler = Scheduler(owner=owner, pet=pet)

        for task in st.session_state.tasks:
            scheduler.add_task(task)

        scheduler.generate_plan()

        # ── Schedule summary metrics ──────────────────────────────────────
        scheduled_count = len(scheduler.scheduled_tasks)
        skipped_count = sum(
            1 for t in scheduler.tasks if t.status == "skipped"
        )
        used_min = scheduler.total_duration
        avail_min = owner.get_available_time()
        pct = round(used_min / avail_min * 100) if avail_min else 0

        if scheduled_count:
            st.success(
                f"Schedule generated for **{pet_name}** — "
                f"{scheduled_count} task(s) scheduled, "
                f"{used_min} / {avail_min} min used ({pct} %)."
            )
        else:
            st.warning("No tasks could be scheduled. Check your available time.")

        if skipped_count:
            st.warning(
                f"{skipped_count} task(s) skipped — not enough time after higher-priority tasks."
            )

        s1, s2, s3 = st.columns(3)
        s1.metric("Scheduled", scheduled_count)
        s2.metric("Skipped", skipped_count)
        s3.metric("Time used (min)", f"{used_min} / {avail_min}")

        # ── Scheduled tasks table ─────────────────────────────────────────
        if scheduler.scheduled_tasks:
            st.markdown("#### Daily schedule")
            _PRIORITY_ICON = {"high": "🔴 high", "medium": "🟡 medium", "low": "🟢 low"}

            st.table(
                [
                    {
                        "#": i,
                        "Task": t.title,
                        "Start": _fmt_time(t.start_time) if t.start_time is not None else "—",
                        "End": _fmt_time(t.end_time) if t.end_time is not None else "—",
                        "Duration (min)": t.duration_minutes,
                        "Priority": _PRIORITY_ICON.get(t.priority, t.priority),
                        "Recurrence": f"↻ {t.recurrence}" if t.recurrence else "—",
                    }
                    for i, t in enumerate(scheduler.sort_by_time(), start=1)
                ]
            )

        # ── Conflicts ─────────────────────────────────────────────────────
        if scheduler.conflicts:
            st.markdown("#### ⚠️ Conflicts detected")
            for a, b in scheduler.conflicts:
                st.warning(
                    f"**'{a.title}'** ({_fmt_time(a.start_time)}–{_fmt_time(a.end_time)}) "
                    f"overlaps with **'{b.title}'** "
                    f"({_fmt_time(b.start_time)}–{_fmt_time(b.end_time)})"
                )

        # ── Upcoming recurring tasks ───────────────────────────────────────
        recurring = scheduler.next_recurring_tasks()
        if recurring:
            st.divider()
            st.markdown("#### Upcoming recurring tasks")
            st.table(
                [
                    {"Task": t.title, "Recurrence": t.recurrence, "Next date": str(d)}
                    for t, d in recurring
                ]
            )

        # ── Mark task done ────────────────────────────────────────────────
        st.divider()
        st.markdown("#### Mark a task as done")
        pending_titles = [t.title for t in scheduler.scheduled_tasks if t.status != "done"]
        if pending_titles:
            done_title = st.selectbox("Select completed task", pending_titles, key="mark_done_select")
            if st.button("Mark done"):
                next_task = scheduler.mark_task_done(done_title)
                st.session_state.tasks = scheduler.tasks
                if next_task:
                    st.success(
                        f"'{done_title}' marked done. "
                        f"Next {next_task.recurrence} occurrence added for {next_task.due_date}."
                    )
                else:
                    st.success(f"'{done_title}' marked done.")
                st.rerun()
        else:
            st.success("All scheduled tasks are done.")

        # ── Plan explanation ──────────────────────────────────────────────
        st.divider()
        st.markdown("#### Why was each task chosen?")

        for title, reason in scheduler.explanations.items():
            if reason.startswith("Included"):
                st.success(f"**{title}** — {reason}")
            else:
                st.warning(f"**{title}** — {reason}")
