from xmlrpc.client import boolean
from sqlmodel import SQLModel, Field
from datetime import datetime
from typing_extensions import Annotated

class Todos(SQLModel, table=True):
  id: int |None = Field(default=None, primary_key=True)
  name: Annotated[str, Field(max_length=20)]
  isComplete: boolean = Field(default=False, nullable=False)
  created_at: datetime = Field(default_factory=datetime.now)
  updated_at: datetime = Field(default_factory=datetime.now)
