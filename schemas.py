from datetime import date as date_type
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

Category = Literal["strength", "cardio"]
WeightUnit = Literal["lb", "kg"]


def _strip(value):
    """Trim whitespace from strings; turn blank strings into None."""
    if isinstance(value, str):
        value = value.strip()
        return value or None
    return value


# ---------- Exercise catalog ----------

class ExerciseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    category: Category
    muscle_group: Optional[str] = None
    equipment: Optional[str] = None

    @field_validator("name", "muscle_group", "equipment", mode="before")
    @classmethod
    def strip_text(cls, value):
        return _strip(value)


class ExerciseOut(ExerciseCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    is_custom: bool


# ---------- Sets ----------

class SetCreate(BaseModel):
    reps: Optional[int] = Field(default=None, ge=1)
    weight: Optional[float] = Field(default=None, ge=0)
    duration_seconds: Optional[int] = Field(default=None, ge=1)
    distance: Optional[float] = Field(default=None, gt=0)
    pace_per_mile: Optional[str] = Field(default=None, max_length=20)
    is_warmup: bool = False

    @field_validator("pace_per_mile", mode="before")
    @classmethod
    def strip_pace(cls, value):
        return _strip(value)

    @model_validator(mode="after")
    def needs_a_measurement(self):
        if (
            self.reps is None
            and self.duration_seconds is None
            and self.distance is None
            and self.pace_per_mile is None
        ):
            raise ValueError(
                "each set needs at least one of: reps, duration_seconds, distance, pace_per_mile"
            )
        return self


class SetOut(SetCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    set_number: int


# ---------- Workout exercises ----------

class WorkoutExerciseCreate(BaseModel):
    exercise_id: int
    notes: Optional[str] = None
    sets: list[SetCreate] = Field(min_length=1)

    @field_validator("notes", mode="before")
    @classmethod
    def strip_text(cls, value):
        return _strip(value)


class WorkoutExerciseOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    notes: Optional[str]
    exercise: ExerciseOut
    sets: list[SetOut]


# ---------- Workouts ----------

class WorkoutCreate(BaseModel):
    date: date_type
    title: Optional[str] = None
    duration_minutes: Optional[int] = Field(default=None, ge=1)
    intensity: Optional[int] = Field(default=None, ge=0, le=100)
    weight_unit: WeightUnit = "lb"
    notes: Optional[str] = None
    exercises: list[WorkoutExerciseCreate] = Field(min_length=1)

    @field_validator("title", "notes", mode="before")
    @classmethod
    def strip_text(cls, value):
        return _strip(value)


class WorkoutOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    date: date_type
    title: Optional[str]
    duration_minutes: Optional[int]
    intensity: Optional[int]
    weight_unit: WeightUnit
    notes: Optional[str]
    exercises: list[WorkoutExerciseOut]
