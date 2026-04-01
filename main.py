from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner
owner = Owner(name="Jordan", available_minutes=90)

# Create two pets
mochi = Pet(name="Mochi", species="dog", owner=owner)
luna = Pet(name="Luna", species="cat", owner=owner)

# --- Mochi's schedule ---
mochi_scheduler = Scheduler(owner=owner, pet=mochi)
mochi_scheduler.add_task(Task("Morning walk", duration_minutes=30, priority="high"))
mochi_scheduler.add_task(Task("Feeding", duration_minutes=10, priority="high"))
mochi_scheduler.add_task(Task("Grooming", duration_minutes=45, priority="low"))
mochi_scheduler.generate_plan()

# --- Luna's schedule ---
luna_scheduler = Scheduler(owner=owner, pet=luna)
luna_scheduler.add_task(Task("Feeding", duration_minutes=10, priority="high"))
luna_scheduler.add_task(Task("Playtime", duration_minutes=20, priority="medium"))
luna_scheduler.add_task(Task("Vet check-in", duration_minutes=60, priority="high"))
luna_scheduler.generate_plan()

# --- Print today's schedule ---
print("=" * 40)
print("        TODAY'S SCHEDULE")
print("=" * 40)

print(f"\n>> {mochi.get_info()}")
print(mochi_scheduler.display_plan())
print()
print(mochi_scheduler.explain_plan())

print("\n" + "-" * 40)

print(f"\n>> {luna.get_info()}")
print(luna_scheduler.display_plan())
print()
print(luna_scheduler.explain_plan())

print("\n" + "=" * 40)
