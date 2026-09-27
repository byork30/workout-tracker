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
    sets = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight = Column(Float, nullable=True)

    workout = relationship("Workout", back_populates="exercises")
