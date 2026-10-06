from datetime import datetime

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field, model_validator
from typing import List
from fastapi import Query


class PayloadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    output: str = Field(validation_alias=AliasChoices("text", "output"))


class PayloadCreate(BaseModel):
    list1: List[str] = Field(..., description="List 1 of strings to be processed")
    list2: List[str] = Field(..., description="List 2 of strings to be processed")

    @model_validator(mode="after")
    def lists_should_be_equal_length(self):
        if len(self.list1) != len(self.list2):
            raise ValueError("list1 and list2 must have the same length")
        return self


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    is_completed: bool = False


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    is_completed: bool | None = None


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    is_completed: bool
    owner_id: int
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
