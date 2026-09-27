from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

import models
import schemas
from database import engine, get_db

# Creates workouts.db and the tables if they don't exist yet.
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workout Tracker")


@app.post("/workouts", response_model=schemas.WorkoutOut)
def create_workout(workout: schemas.WorkoutCreate, db: Session = Depends(get_db)):
    """Create a workout along with all of its exercises in one request."""
    db_workout = models.Workout(date=workout.date, notes=workout.notes)
    for exercise in workout.exercises:
        db_workout.exercises.append(models.Exercise(**exercise.model_dump()))

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
