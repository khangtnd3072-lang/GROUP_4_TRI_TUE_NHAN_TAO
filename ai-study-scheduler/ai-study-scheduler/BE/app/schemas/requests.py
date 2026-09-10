from datetime import date, datetime, time
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, field_validator


class SubjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    priority: int = Field(default=3, ge=1, le=5)
    difficulty: int = Field(default=3, ge=1, le=5)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Tên môn học không được để trống")
        return value


class TaskCreate(BaseModel):
    subject_id: int = Field(gt=0)
    title: str = Field(min_length=1, max_length=180)
    estimated_hours: float = Field(ge=0.5, le=200)
    deadline: datetime
    priority: int = Field(default=3, ge=1, le=5)
    difficulty: int = Field(default=3, ge=1, le=5)
    notes: str | None = Field(default=None, max_length=5000)
    resource_link: HttpUrl | None = None

    @field_validator("title")
    @classmethod
    def clean_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Tên công việc không được để trống")
        return value


class TaskStatusUpdate(BaseModel):
    status: Literal["pending", "in_progress", "completed"]


class AvailabilityCreate(BaseModel):
    study_date: date
    start_time: time
    end_time: time

    @field_validator("end_time")
    @classmethod
    def validate_time_range(cls, value: time, info):
        start = info.data.get("start_time")
        if start is not None and value <= start:
            raise ValueError("Giờ kết thúc phải sau giờ bắt đầu")
        return value


class SessionStatusUpdate(BaseModel):
    status: Literal["planned", "completed", "missed"]
