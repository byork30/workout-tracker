from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    notes = Column(String, nullable=True)

    # One workout has many exercises. Deleting a workout deletes its exercises too.
    exercises = relationship(
        "Exercise", back_populates="workout", cascade="all, delete-orphan"
    )


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    workout_id = Column(Integer, ForeignKey("workouts.id"), nullable=False)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False, default="strength")
    sets = Column(Integer, nullable=True)
    reps = Column(Integer, nullable=True)
    weight = Column(Float, nullable=True)
    intensity = Column(Integer, nullable=True, default=0)
    rest_seconds = Column(Integer, nullable=True)
    time_minutes = Column(Integer, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    distance_miles = Column(Float, nullable=True)
    pace_per_mile = Column(String, nullable=True)
    notes = Column(String, nullable=True)

    workout = relationship("Workout", back_populates="exercises")
