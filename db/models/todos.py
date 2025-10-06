from sqlmodel import SQLModel, Field
from datetime import datetime

class Todos(SQLModel, table=True):
  id: int |None = Field(default=None, primary_key=True)
  name: str = Field(nullable=False)
  created_at: datetime = Field(default_factory=datetime.now)
  updated_at: datetime = Field(default_factory=datetime.now)
