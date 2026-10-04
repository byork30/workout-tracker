"""Populates the exercise catalog with common exercises.

Safe to run repeatedly: it only inserts exercises whose names aren't already
in the database, so you can add to SEED_EXERCISES later and re-run it.

The app also calls seed_exercises() on startup, but you can run this file
directly too:  python seed.py
"""
from sqlalchemy import func

import models
from database import Base, SessionLocal, engine

# (name, category, muscle_group, equipment)
SEED_EXERCISES = [
    # Chest
    ("Bench Press", "strength", "chest", "barbell"),
    ("Incline Dumbbell Press", "strength", "chest", "dumbbell"),
    ("Dumbbell Fly", "strength", "chest", "dumbbell"),
    ("Push-Up", "strength", "chest", "bodyweight"),
    ("Dips", "strength", "triceps", "bodyweight"),
    # Shoulders
    ("Overhead Press", "strength", "shoulders", "barbell"),
    ("Lateral Raise", "strength", "shoulders", "dumbbell"),
    ("Face Pull", "strength", "shoulders", "cable"),
    # Arms
    ("Barbell Curl", "strength", "biceps", "barbell"),
    ("Hammer Curl", "strength", "biceps", "dumbbell"),
    ("Tricep Pushdown", "strength", "triceps", "cable"),
    ("Skull Crusher", "strength", "triceps", "barbell"),
    ("Overhead Tricep Extension", "strength", "triceps", "dumbbell"),
    # Back
    ("Pull-Up", "strength", "lats", "bodyweight"),
    ("Chin-Up", "strength", "lats", "bodyweight"),
    ("Lat Pulldown", "strength", "lats", "cable"),
    ("Barbell Row", "strength", "middle_back", "barbell"),
    ("Seated Cable Row", "strength", "middle_back", "cable"),
    ("Dumbbell Row", "strength", "middle_back", "dumbbell"),
    ("Deadlift", "strength", "lower_back", "barbell"),
    # Legs
    ("Back Squat", "strength", "quadriceps", "barbell"),
    ("Front Squat", "strength", "quadriceps", "barbell"),
    ("Leg Press", "strength", "quadriceps", "machine"),
    ("Leg Extension", "strength", "quadriceps", "machine"),
    ("Walking Lunge", "strength", "quadriceps", "dumbbell"),
    ("Bulgarian Split Squat", "strength", "quadriceps", "dumbbell"),
    ("Romanian Deadlift", "strength", "hamstrings", "barbell"),
    ("Leg Curl", "strength", "hamstrings", "machine"),
    ("Hip Thrust", "strength", "glutes", "barbell"),
    ("Standing Calf Raise", "strength", "calves", "machine"),
    # Core
    ("Cable Crunch", "strength", "abdominals", "cable"),
    ("Hanging Leg Raise", "strength", "abdominals", "bodyweight"),
    # Cardio
    ("Running", "cardio", None, None),
    ("Walking", "cardio", None, None),
    ("Hiking", "cardio", None, None),
    ("Cycling", "cardio", None, "bike"),
    ("Rowing Machine", "cardio", None, "machine"),
    ("Swimming", "cardio", None, None),
    ("Jump Rope", "cardio", None, "jump rope"),
    ("Stair Climber", "cardio", None, "machine"),
    ("Elliptical", "cardio", None, "machine"),
    ("Burpees", "cardio", "full_body", "bodyweight"),
]


def seed_exercises(db):
    """Insert any catalog exercises that don't exist yet. Returns how many were added."""
    existing = {
        name.lower() for (name,) in db.query(func.lower(models.Exercise.name)).all()
    }
    added = 0
    for name, category, muscle_group, equipment in SEED_EXERCISES:
        if name.lower() in existing:
            continue
        db.add(
            models.Exercise(
                name=name,
                category=category,
                muscle_group=muscle_group,
                equipment=equipment,
                is_custom=False,
            )
        )
        added += 1
    db.commit()
    return added


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        count = seed_exercises(session)
    finally:
        session.close()
    print(f"Added {count} exercises.")
