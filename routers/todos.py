from typing import Annotated
from fastapi import APIRouter, Request, Query, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound # 若 ORM 找不到資料時，引發的錯誤類
from db.models import get_session
from sqlmodel import select, text
from db.models.todos import Todos
from tool.message import flash_message
from middlewares.isauthenticated import isAuthemticated
from routers.users import sessions


# 加入 dependencies，每個路由執行前都會先執行 isAuthemticated 函式作驗證
todos = APIRouter(prefix="/todos", dependencies=[Depends(isAuthemticated)])

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
  limit: Annotated[int, Query(le=100)] = 10,
  page: int = Query(default=1)
) :

  print(request.state.user)
  print(sessions)
  
  # 每頁顯示的 todo 數量
  LIMIT = 10 

  # todo 總數量
  result = await session.execute(text("select count(*) from todos"))
  total_todos = result.scalar() or 0

  # 總頁數，確保大於 0
  total_page = total_todos // LIMIT if total_todos // LIMIT > 0 else 1

  # 目前頁面
  if page < 1 : page = 1
  if page > total_page : page = total_page

  # 計算偏移量
  offset = (page - 1) * 10

  result = await session.execute(select(Todos.id, Todos.name, Todos.isComplete).offset(offset).limit(limit))

  todos = [{'id': todo[0], 'name':todo[1], "completed": todo[2]} for todo in result.all() ]

  page_info = {}

  page_info["page"] = page

  return templates.TemplateResponse(request, 'todos.html', {'todos' : todos, 'message': request.state.message, "page_info":page_info})



"""
新增 todos 頁面路由
"""
@todos.get("/new")
async def get_todos_new_page(request: Request):

  return templates.TemplateResponse(request, "new.html", {'message': request.state.message})



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
  if len(name) > 20 :
    flash_message(request, "新增 Todo 失敗 : Name 長度不能超過 20", "error")
    raise Exception()

  session.add(Todos(name= name))
  await session.commit()

  flash_message(request, "成功建立 Todo!", "success")

  return RedirectResponse("/todos/", status_code=303)



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

  # 找不到 todo 時，異常處理
  except NoResultFound as e :
    flash_message(request, "找不到 Todo!", "error")
    raise e

  result = {"id" : result[0], "name": result[1], "completed": result[2]}

  return templates.TemplateResponse(request, "todo.html", {"todo" : result, "message": request.state.message})



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
    flash_message(request, "無此 todo 可編輯!", "error")
    raise e

  result = {"id": result[0], "name": result[1], "completed": result[2]}

  return templates.TemplateResponse(request, "edit.html", {"todo" : result, "message" : request.state.message})



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
    if len(name) > 20 :
      flash_message(request, "新增 Todo 失敗 : Name 長度不能超過 20", "error")
      raise Exception()

    """ 先 select 要修改的 todo，並建立 instance"""
    statement = select(Todos).where(Todos.id == id)
    result = await session.execute(statement)
    todo = result.scalars().one()

    """ 接著修改 instance 的 name，再新增 """
    todo.name = name
    todo.isComplete = bool(completed)
  
  except NoResultFound as e:
    flash_message(request, "無此 todo 可編輯! ", "error")
    raise e

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
    flash_message(request, "無此 todo 可刪除! ", "error")
    raise e

  await session.delete(todo)
  await session.commit()

  flash_message(request, "成功刪除資料", "success")

  return RedirectResponse("/todos/", status_code=303)
