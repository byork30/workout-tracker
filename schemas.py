from datetime import date as date_type
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ExerciseCreate(BaseModel):
    name: str
    category: str = "strength"
    sets: Optional[int] = None
    reps: Optional[int] = None
    weight: Optional[float] = None
    intensity: Optional[int] = Field(default=None, ge=0, le=100)
    rest_seconds: Optional[int] = None
    time_minutes: Optional[int] = None
    duration_minutes: Optional[int] = None
    distance_miles: Optional[float] = None
    pace_per_mile: Optional[str] = None
    notes: Optional[str] = None

    @model_validator(mode="after")
    def validate_exercise_fields(self):
        if self.category not in {"strength", "cardio"}:
            raise ValueError("Exercise category must be 'strength' or 'cardio'.")
        return self


class ExerciseOut(ExerciseCreate):
    id: int
    model_config = ConfigDict(from_attributes=True)


class WorkoutCreate(BaseModel):
    date: date_type
    notes: Optional[str] = None
    exercises: list[ExerciseCreate]


class WorkoutOut(BaseModel):
    id: int
    date: date_type
    notes: Optional[str]
    exercises: list[ExerciseOut]
    model_config = ConfigDict(from_attributes=True)
