from typing import Annotated
from fastapi import APIRouter, Request, Query, Depends, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound # 若 ORM 找不到資料時，引發的錯誤類
from db.models import get_session
from sqlmodel import select
from db.models.todos import Todos
from tool.tools import flash_message, get_flash_message

todos = APIRouter(prefix="/todos")

templates = Jinja2Templates(directory="templates")

SessionDep = Annotated[AsyncSession, Depends(get_session)]

"""
查看所有 todos 路由
"""
@todos.get("/")
async def get_todos(
  request: Request,
  session: SessionDep,
  offset: int = 0,
  limit: Annotated[int, Query(le=100)] = 100
) :
  result = await session.execute(select(Todos.id, Todos.name, Todos.isComplete).offset(offset).limit(limit))

  todos = [{'id': todo[0], 'name':todo[1], "completed": todo[2]} for todo in result.all() ]

  message = get_flash_message(request) 

  return templates.TemplateResponse(request, 'todos.html', {'todos' : todos, 'message': message})

@todos.get("/new")
async def get_todos_new_page(request: Request):
  message = get_flash_message(request) 

  return templates.TemplateResponse(request, "new.html", {'message': message})


"""
新增 todo 路由
"""
@todos.post("/")
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
  await session.commit()

  flash_message(request, "成功建立 Todo!", "success")

  return RedirectResponse("/todos", status_code=303)


"""
查看單筆 todo 路由
"""
@todos.get("/{id}")
async def get_todos_detail(
  request: Request,
  id: int,
  session: SessionDep
):
  todo_detail = select(Todos.id, Todos.name, Todos.isComplete).where(Todos.id == id)

  """ 檢查是否有此 todo """
  try:
    result = await session.execute(todo_detail)
    result = result.one()

  except NoResultFound as e :
    print(e)

    flash_message(request, "找不到 Todo!", "error")

    return RedirectResponse("/todos", status_code=303)


  result = {"id" : result[0], "name": result[1], "completed": result[2]}

  message = get_flash_message(request)

  return templates.TemplateResponse(request, "todo.html", {"todo" : result, "message": message})


"""
取得編輯 todo 路由
"""
@todos.get("/{id}/edit")
async def get_todos_edit_page(
  id: int,
  request: Request,
  session: SessionDep
):
  todo = select(Todos.id, Todos.name, Todos.isComplete).where(Todos.id == id)

  """ 檢查是否有此 todo """
  try:
    result = await session.execute(todo)
    result = result.one()

  except NoResultFound as e :
    print(e)

    flash_message(request, "無此 todo 可編輯!", "error")

    return RedirectResponse("/todos", status_code=303)

  result = {"id": result[0], "name": result[1], "completed": result[2]}

  message = get_flash_message(request)

  return templates.TemplateResponse(request, "edit.html", {"todo" : result, "message" : message})


"""
編輯 todo 路由
"""
@todos.put("/{id}")
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
    result = await session.execute(statement)
    todo = result.scalars().one()

    print(todo)

    """ 接著修改 instance 的 name，再新增 """
    todo.name = name
    todo.isComplete = bool(completed)

  except HTTPException as e:
    flash_message(request, f"修改 Todo 失敗 : { e.detail }", "error")

    prev_url = request.headers.get("referer") or "/"

    return RedirectResponse(prev_url, status_code=303)
  
  except NoResultFound as e:
    flash_message(request, "無此 todo 可編輯! ", "error")

    prev_url = request.headers.get("referer") or "/todos"

    return RedirectResponse(prev_url, status_code=303)

  await session.commit()

  flash_message(request, "成功修改資料", "success")

  return RedirectResponse(f"/todos/{id}", status_code=303)


"""
刪除 todo 路由
"""
@todos.delete("/{id}")
async def delete_todos(
  request: Request,
  id: int,
  session: SessionDep
):

  statement = select(Todos).where(Todos.id == id)

  try:
    result = await session.execute(statement)

    todo = result.scalars().one()

  except NoResultFound as e:
    print(e)

    flash_message(request, "無此 todo 可刪除! ", "error")

    prev_url = request.headers.get("referer") or "/todos"

    return RedirectResponse(prev_url, status_code=303)

  await session.delete(todo)
  await session.commit()

  flash_message(request, "成功刪除資料", "success")

  return RedirectResponse("/todos", status_code=303)