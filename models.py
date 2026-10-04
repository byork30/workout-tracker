from sqlalchemy import Column, Integer, String, Float, Date, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Exercise(Base):
    """A catalog entry: something you can log (e.g. "Bench Press", "Running")."""

    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    category = Column(String, nullable=False)  # "strength" or "cardio"
    muscle_group = Column(String, nullable=True)
    equipment = Column(String, nullable=True)
    is_custom = Column(Boolean, nullable=False, default=False)


class Workout(Base):
    """One training session."""

    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    title = Column(String, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    intensity = Column(Integer, nullable=True)  # the user's own 0-100 rating
    weight_unit = Column(String, nullable=False, default="lb")  # "lb" or "kg"
    notes = Column(String, nullable=True)

    # Named "exercises" so the API's JSON reads naturally. Each item is a
    # WorkoutExercise: one catalog exercise as performed in this workout.
    exercises = relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.position",
    )


class WorkoutExercise(Base):
    """Links a workout to a catalog exercise and holds that exercise's sets."""

    __tablename__ = "workout_exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    position = Column(Integer, nullable=False, default=1)  # order within the workout
    notes = Column(String, nullable=True)

    workout = relationship("Workout", back_populates="exercises")
    exercise = relationship("Exercise")
    sets = relationship(
        "WorkoutSet",
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
        order_by="WorkoutSet.set_number",
    )


class WorkoutSet(Base):
    """One set (or one cardio interval). Every measurement is optional so the
    same table covers lifting, bodyweight work, and cardio."""

    __tablename__ = "sets"

    id = Column(Integer, primary_key=True, index=True)
    workout_exercise_id = Column(
        Integer, ForeignKey("workout_exercises.id"), nullable=False
    )
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    duration_seconds = Column(Integer, nullable=True)
    distance = Column(Float, nullable=True)  # mi or km, following the workout's unit
    pace_per_mile = Column(String, nullable=True)  # free text, e.g. "8:45" - independent of duration/distance since either can be logged alone
    is_warmup = Column(Boolean, nullable=False, default=False)

    workout_exercise = relationship("WorkoutExercise", back_populates="sets")
