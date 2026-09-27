from datetime import date as date_type
from typing import Optional

from pydantic import BaseModel


class ExerciseCreate(BaseModel):
    name: str
    sets: int
    reps: int
    weight: Optional[float] = None


class ExerciseOut(ExerciseCreate):
    id: int

    class Config:
        from_attributes = True  # lets Pydantic read data straight from SQLAlchemy models


class WorkoutCreate(BaseModel):
    date: date_type
    notes: Optional[str] = None
    exercises: list[ExerciseCreate]


class WorkoutOut(BaseModel):
    id: int
    date: date_type
    notes: Optional[str]
    exercises: list[ExerciseOut]

    class Config:
        from_attributes = True
