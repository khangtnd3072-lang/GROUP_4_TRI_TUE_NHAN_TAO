from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class StudyTask:
    id: int
    subject_id: int
    title: str
    subject_name: str
    estimated_hours: float
    deadline: datetime
    priority: int
    difficulty: int


@dataclass(frozen=True)
class TimeSlot:
    index: int
    start: datetime
    end: datetime

    @property
    def date_key(self):
        return self.start.date()
