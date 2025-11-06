from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Annotated

class Todos(SQLModel, table=True):
  id: int |None = Field(default=None, primary_key=True)
  name: Annotated[str, Field(max_length=20)]
  isComplete: bool = Field(default=False, nullable=False)
  user_id: int | None =Field(default=None, foreign_key="users.id", nullable=False)
  created_at: datetime = Field(default_factory=datetime.now)
  updated_at: datetime = Field(default_factory=datetime.now)
