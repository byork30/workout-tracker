from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db


def ensure_exercise_columns():
    """Upgrade legacy exercise tables so strength and cardio entries can coexist."""
    inspector = inspect(engine)
    if not inspector.has_table("exercises"):
        models.Base.metadata.create_all(bind=engine)
        return

    columns = inspector.get_columns("exercises")
    existing_columns = {column["name"]: column for column in columns}

    needs_rebuild = (
        "category" not in existing_columns
        or "duration_minutes" not in existing_columns
        or "time_minutes" not in existing_columns
        or existing_columns.get("sets", {}).get("nullable") is False
        or existing_columns.get("reps", {}).get("nullable") is False
    )

    if not needs_rebuild:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE exercises RENAME TO exercises_old"))

    models.Base.metadata.create_all(bind=engine)

    with engine.begin() as connection:
        connection.execute(
            text(
                """
                INSERT INTO exercises (
                    id, workout_id, name, category, sets, reps, weight,
                    intensity, rest_seconds, time_minutes, duration_minutes,
                    distance_miles, pace_per_mile, notes
                )
                SELECT
                    id, workout_id, name,
                    COALESCE(category, 'strength'),
                    sets, reps, weight,
                    COALESCE(intensity, 0), rest_seconds, NULL, duration_minutes,
                    distance_miles, pace_per_mile, notes
                FROM exercises_old
                """
            )
        )
        connection.execute(text("DROP TABLE exercises_old"))


ensure_exercise_columns()

app = FastAPI(title="Workout Tracker")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/workouts", response_model=schemas.WorkoutOut)
def create_workout(workout: schemas.WorkoutCreate, db: Session = Depends(get_db)):
    """Create a workout along with all of its exercises in one request."""
    db_workout = models.Workout(date=workout.date, notes=workout.notes)
    for exercise in workout.exercises:
        db_workout.exercises.append(models.Exercise(**exercise.model_dump(exclude_none=True)))

    db.add(db_workout)
    db.commit()
    db.refresh(db_workout)
    return db_workout


@app.get("/workouts", response_model=list[schemas.WorkoutOut])
def list_workouts(db: Session = Depends(get_db)):
    """Return all workouts, most recent first."""
    return db.query(models.Workout).order_by(models.Workout.date.desc()).all()


@app.get("/workouts/{workout_id}", response_model=schemas.WorkoutOut)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    """Return a single workout by id, or 404 if it doesn't exist."""
    workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@app.put("/workouts/{workout_id}", response_model=schemas.WorkoutOut)
def update_workout(workout_id: int, workout: schemas.WorkoutCreate, db: Session = Depends(get_db)):
    """Replace a workout and its exercises with updated values."""
    db_workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")

    db_workout.date = workout.date
    db_workout.notes = workout.notes
    db_workout.exercises.clear()
    for exercise in workout.exercises:
        db_workout.exercises.append(models.Exercise(**exercise.model_dump(exclude_none=True)))

    db.commit()
    db.refresh(db_workout)
    return db_workout


@app.delete("/workouts/{workout_id}")
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    """Delete a workout by id."""
    workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")

    db.delete(workout)
    db.commit()
    return {"detail": "Workout deleted"}
