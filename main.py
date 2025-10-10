from typing import Annotated
from fastapi import FastAPI, Query, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from sqlalchemy.exc import NoResultFound # 若 ORM 找不到資料時，引發的錯誤類
from db.models import get_session
from db.models.todos import Todos
from starlette.middleware.sessions import SessionMiddleware
from tool.tools import flash_message, get_flash_message

templates = Jinja2Templates(directory="templates")

app = FastAPI()

# 自動在 request 中加入 session 並簽名
app.add_middleware(SessionMiddleware, secret_key="secret")

SessionDep = Annotated[Session, Depends(get_session)]


""" middleware，每一個 HTTP 請求進來時先進來這個 middleware，再分配要進到哪一個路由 """
@app.middleware("http")
async def method_override(
  request: Request,
  call_next
):
  if request.method == "POST":
    form = await request.form()
    method = form.get("_method") or "POST"
    if method:
        request.scope["method"] = str(method).upper()  # 改變 HTTP 方法

    request.state.form = form
  response = await call_next(request)
  return response


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
  todos = session.exec(select(Todos.id, Todos.name, Todos.isComplete).offset(offset).limit(limit)).all()

  todos = [{'id': todo[0], 'name':todo[1], "completed": todo[2]} for todo in todos ]

  message = get_flash_message(request) 

  return templates.TemplateResponse(request, 'todos.html', {'todos' : todos, 'message': message})

@app.get("/todos/new")
async def get_todos_new_page(request: Request):
  message = get_flash_message(request) 

  return templates.TemplateResponse(request, "new.html", {'message': message})

@app.post("/todos")
async def create_todos(
  request: Request,
  session: SessionDep,
):
  form = request.state.form
  name = form.get("name")

  """ 檢查 name 長度 """
  try :
    if len(name) > 20 : raise HTTPException(status_code=400, detail="Name 長度不能超過 20")

  except HTTPException as e:
    flash_message(request, f"新增 Todo 失敗 : { e.detail }", "error")

    prev_url = request.headers.get("referer") or "/"

    return RedirectResponse(prev_url, status_code=303)

  session.add(Todos(name= name))
  session.commit()

  flash_message(request, "成功建立 Todo!", "success")

  return RedirectResponse("/todos", status_code=303)

@app.get("/todos/{id}")
async def get_todos_detail(
  request: Request,
  id: int,
  session: SessionDep
):
  todo_detail = select(Todos.id, Todos.name, Todos.isComplete).where(Todos.id == id)

  """ 檢查是否有此 todo """
  try:
    result = session.exec(todo_detail).one()

  except NoResultFound as e :
    print(e)

    flash_message(request, "找不到 Todo!", "error")

    return RedirectResponse("/todos", status_code=303)


  result = {"id" : result[0], "name": result[1], "completed": result[2]}

  message = get_flash_message(request)

  return templates.TemplateResponse(request, "todo.html", {"todo" : result, "message": message})

@app.get("/todos/{id}/edit")
async def get_todos_edit_page(
  id: int,
  request: Request,
  session: SessionDep
):
  todo = select(Todos.id, Todos.name, Todos.isComplete).where(Todos.id == id)

  """ 檢查是否有此 todo """
  try:
    result = session.exec(todo).one()

  except NoResultFound as e :
    print(e)

    flash_message(request, "無此 todo 可編輯!", "error")

    return RedirectResponse("/todos", status_code=303)

  result = {"id": result[0], "name": result[1], "completed": result[2]}

  message = get_flash_message(request)

  return templates.TemplateResponse(request, "edit.html", {"todo" : result, "message" : message})

@app.put("/todos/{id}")
async def update_todos(
  request: Request,
  session: SessionDep,
  id: int,
):
  form = request.state.form
  name = form.get("name")
  completed = form.get("completed")

  """ 檢查 name 長度 """
  try :
    if len(name) > 20 : raise HTTPException(status_code=400, detail="Name 長度不能超過 20")

    """ 先 select 要修改的 todo，並建立 instance"""
    statement = select(Todos).where(Todos.id == id)
    todo = session.exec(statement).one()

  except HTTPException as e:
    flash_message(request, f"修改 Todo 失敗 : { e.detail }", "error")

    prev_url = request.headers.get("referer") or "/"

    return RedirectResponse(prev_url, status_code=303)
  
  except NoResultFound as e:
    flash_message(request, "無此 todo 可編輯! ", "error")

    prev_url = request.headers.get("referer") or "/todos"

    return RedirectResponse(prev_url, status_code=303)


  """ 接著修改 instance 的 name，再新增 """
  todo.name = name
  todo.isComplete = bool(completed)
  session.add(todo)
  session.commit()

  flash_message(request, "成功修改資料", "success")

  return RedirectResponse(f"/todos/{id}", status_code=303)

@app.delete("/todos/{id}")
async def delete_todos(
  request: Request,
  id: int,
  session: SessionDep
):

  statement = select(Todos).where(Todos.id == id)

  try:
    todo = session.exec(statement).one()

  except NoResultFound as e:
    print(e)

    flash_message(request, "無此 todo 可刪除! ", "error")

    prev_url = request.headers.get("referer") or "/todos"

    return RedirectResponse(prev_url, status_code=303)

  session.delete(todo)
  session.commit()

  flash_message(request, "成功刪除資料", "success")

  return RedirectResponse("/todos", status_code=303)
  