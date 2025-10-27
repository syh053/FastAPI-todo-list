from typing import Annotated
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from db.models import get_session
from tool.tools import flash_message
from db.models.users import Users

users = APIRouter(prefix="/users")

templates = Jinja2Templates(directory="templates")

sessionDep = Annotated[AsyncSession, Depends(get_session)]

@users.get("/login")
async def login_page(
  request: Request
):
  return templates.TemplateResponse("login.html", {"request" : request, "message": request.state.message})


@users.get("/register")
async def register_page(
  request: Request
):
  return templates.TemplateResponse("register.html", {"request": request, "message": request.state.message})


@users.post("/login")
async def login(
  request: Request
): 
  form = request.state.form # 讀取表單訊息
  email = form.get("email") # 讀取 email
  password = form.get("password") # 讀取 password

  print(email)
  print(password)

  return RedirectResponse("/todos/", status_code=303)


@users.post("/register")
async def register(
  request: Request,
  session: sessionDep
):
  form = request.state.form # 讀取表單訊息
  email = form.get("email") # 讀取 email
  password = form.get("password", None) # 讀取 password
  confirm_password = form.get("confirm_password", None) # 讀取確認 password
  name = form.get("name")

  
  # 若未輸入 email 或 password，就重導向到 register 頁面，並顯示錯誤內容
  if not email or not password :
    flash_message(request, "未輸入 email 或 password", "error")
    return RedirectResponse("/users/register", status_code=303)

  # 若 password 與 confirm_password 輸入不一致，就重導向到 register 頁面，並顯示錯誤內容
  if password != confirm_password :
    flash_message(request, "password 與 confirm_password 輸入不一致", "error")
    return RedirectResponse("/users/register", status_code=303)
  
  # 確認是否已經有 email 註冊
  result = select(Users).where(Users.email == email)
  user = await session.execute(result)
  
  # 若比數大於 0，表示有相同的 mail 註冊過了
  if len(user.all()) > 0 :
    flash_message(request, "該 email 已註冊", "error")
    return RedirectResponse("/users/register", status_code=303)

  # 開始註冊
  session.add(Users(email=email, password=password, name=name))
  await session.commit()

  flash_message(request, "註冊成功", "success")

  return RedirectResponse("/users/login", status_code=303)


@users.post("/logout")
async def logout():
  return RedirectResponse("/users/login", status_code=303)
