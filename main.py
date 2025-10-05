from typing import Annotated
from fastapi import FastAPI, Query, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from db.models import get_session
from db.models.todos import Todos

templates = Jinja2Templates(directory="templates")

app = FastAPI()


SessionDep = Annotated[Session, Depends(get_session)]


@app.get("/")
async def index(request: Request):
  return templates.TemplateResponse(request, 'index.html')

@app.get("/todos")
async def get_todos(
  request: Request,
  session: SessionDep,
  offset: int = 0,
  limit: Annotated[int, Query(le=100)] = 100
) :
  todos = session.exec(select(Todos.id, Todos.name).offset(offset).limit(limit)).all()

  todos = [{'id': todo[0], 'name':todo[1]} for todo in todos ]

  return templates.TemplateResponse(request, 'todos.html', {'todos' : todos})

@app.get("/todos/new")
async def get_todos_new_page():
  return "get todos new page"

@app.post("/todos")
async def create_todos():
  return "add todos"

@app.get("/todos/{id}")
async def get_todos_detail(id: int):
  return f"get todo : {id}"

@app.get("/todos/{id}/edit")
async def get_todos_edit_page(id: int):
  return f"get {id} todos edit page"

@app.put("todos/{id}")
async def update_todos(id: int):
  return f"todos {id} modified"

@app.delete("/todos/{id}")
async def delete_todos(id: int):
  return f"delete {id} todos"
  