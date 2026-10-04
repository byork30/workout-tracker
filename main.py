from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db, SessionLocal
from seed import seed_exercises


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Runs once when the server starts: create any missing tables, then seed
    # the exercise catalog (seed_exercises skips names that already exist).
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_exercises(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Workout Tracker", lifespan=lifespan)

# Lets the frontend (served from a different origin/file) call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Exercise catalog ----------

@app.get("/exercises", response_model=list[schemas.ExerciseOut])
def list_exercises(
    q: Optional[str] = Query(default=None, description="Search by name, partial match"),
    category: Optional[schemas.Category] = None,
    db: Session = Depends(get_db),
):
    """List catalog exercises, optionally filtered by search text and/or category."""
    query = db.query(models.Exercise)
    if q:
        query = query.filter(models.Exercise.name.ilike(f"%{q}%"))
    if category:
        query = query.filter(models.Exercise.category == category)
    return query.order_by(models.Exercise.name).all()


@app.post("/exercises", response_model=schemas.ExerciseOut, status_code=201)
def create_exercise(exercise: schemas.ExerciseCreate, db: Session = Depends(get_db)):
    """Add a custom exercise to the catalog."""
    existing = (
        db.query(models.Exercise)
        .filter(func.lower(models.Exercise.name) == exercise.name.lower())
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f"An exercise named '{existing.name}' already exists",
        )

    db_exercise = models.Exercise(**exercise.model_dump(), is_custom=True)
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise


# ---------- Workouts ----------

def _build_workout_exercises(
    exercises: list[schemas.WorkoutExerciseCreate], db: Session
) -> list[models.WorkoutExercise]:
    """Validates each exercise_id against the catalog and builds the
    WorkoutExercise + WorkoutSet objects for a create/update."""
    built = []
    for position, item in enumerate(exercises, start=1):
        exercise = (
            db.query(models.Exercise)
            .filter(models.Exercise.id == item.exercise_id)
            .first()
        )
        if exercise is None:
            raise HTTPException(
                status_code=400, detail=f"Exercise id {item.exercise_id} not found"
            )

        workout_exercise = models.WorkoutExercise(
            exercise_id=item.exercise_id, position=position, notes=item.notes
        )
        for set_number, set_data in enumerate(item.sets, start=1):
            workout_exercise.sets.append(
                models.WorkoutSet(set_number=set_number, **set_data.model_dump())
            )
        built.append(workout_exercise)
    return built


@app.post("/workouts", response_model=schemas.WorkoutOut, status_code=201)
def create_workout(workout: schemas.WorkoutCreate, db: Session = Depends(get_db)):
    """Create a workout along with all of its exercises and sets in one request."""
    db_workout = models.Workout(
        date=workout.date,
        title=workout.title,
        duration_minutes=workout.duration_minutes,
        intensity=workout.intensity,
        weight_unit=workout.weight_unit,
        notes=workout.notes,
    )
    db_workout.exercises = _build_workout_exercises(workout.exercises, db)

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
def update_workout(
    workout_id: int, workout: schemas.WorkoutCreate, db: Session = Depends(get_db)
):
    """Replace a workout's details and its full list of exercises/sets."""
    db_workout = (
        db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    )
    if db_workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")

    db_workout.date = workout.date
    db_workout.title = workout.title
    db_workout.duration_minutes = workout.duration_minutes
    db_workout.intensity = workout.intensity
    db_workout.weight_unit = workout.weight_unit
    db_workout.notes = workout.notes

    # Clear and flush first so the old rows are actually deleted before the
    # replacements are built, rather than relying on relationship diffing.
    db_workout.exercises.clear()
    db.flush()
    db_workout.exercises = _build_workout_exercises(workout.exercises, db)

    db.commit()
    db.refresh(db_workout)
    return db_workout


@app.delete("/workouts/{workout_id}")
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    """Delete a workout, and its exercises/sets via cascade, by id."""
    workout = db.query(models.Workout).filter(models.Workout.id == workout_id).first()
    if workout is None:
        raise HTTPException(status_code=404, detail="Workout not found")

    db.delete(workout)
    db.commit()
    return {"detail": "Workout deleted"}
