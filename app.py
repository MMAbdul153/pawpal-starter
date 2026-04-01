import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown("Welcome to **PawPal+** — a pet care planning assistant that builds a daily schedule for your pet based on task priority and your available time.")

st.divider()

st.subheader("Owner & Pet Info")

col_a, col_b = st.columns(2)
with col_a:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input("Your available time today (minutes)", min_value=10, max_value=480, value=90)
with col_b:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")

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

if st.session_state.tasks:
    st.write("Current tasks:")

    status_filter = st.selectbox(
        "Filter by status",
        ["all", "pending", "done", "skipped"],
        key="status_filter",
    )

    display_tasks = (
        st.session_state.tasks
        if status_filter == "all"
        else [t for t in st.session_state.tasks if t.status == status_filter]
    )

    if display_tasks:
        st.table([
            {
                "title": t.title,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority,
                "status": t.status,
                "recurrence": t.recurrence or "—",
            }
            for t in display_tasks
        ])
    else:
        st.info(f"No tasks with status '{status_filter}'.")

    if st.button("Clear tasks"):
        st.session_state.tasks = []
        st.rerun()
else:
    st.info("No tasks yet. Add one above.")

st.divider()

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

        st.success("Schedule generated!")
        st.markdown(f"**{scheduler.display_plan()}**")

        if scheduler.conflicts:
            for a, b in scheduler.conflicts:
                from pawpal_system import _fmt_time
                st.warning(
                    f"Conflict: '{a.title}' "
                    f"({_fmt_time(a.start_time)}–{_fmt_time(a.end_time)}) "
                    f"overlaps with '{b.title}' "
                    f"({_fmt_time(b.start_time)}–{_fmt_time(b.end_time)})"
                )

        recurring = scheduler.next_recurring_tasks()
        if recurring:
            st.divider()
            st.markdown("#### Upcoming recurring tasks")
            st.table([
                {"task": t.title, "recurrence": t.recurrence, "next date": str(d)}
                for t, d in recurring
            ])

        st.divider()
        st.markdown("#### Mark a task as done")
        pending_titles = [t.title for t in scheduler.scheduled_tasks if t.status != "done"]
        if pending_titles:
            done_title = st.selectbox("Select completed task", pending_titles, key="mark_done_select")
            if st.button("Mark done"):
                next_task = scheduler.mark_task_done(done_title)
                # Sync changes back to session state
                st.session_state.tasks = scheduler.tasks
                if next_task:
                    st.success(f"'{done_title}' marked done. Next {next_task.recurrence} occurrence added.")
                else:
                    st.success(f"'{done_title}' marked done.")
                st.rerun()
        else:
            st.info("All scheduled tasks are done.")

        st.divider()
        st.markdown("#### Why was each task chosen?")
        st.markdown(scheduler.explain_plan())
