from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Annotated

class Users(SQLModel, table=True):
  id: int | None = Field(default=None, primary_key=True)
  email: Annotated[str, Field(max_length=50, nullable=False)]
  password: Annotated[str, Field(max_length=200, nullable=False)]
  name: Annotated[str, Field(max_length=100)]
  created_at: datetime = Field(default_factory=datetime.now)
  updated_at: datetime = Field(default_factory=datetime.now)
