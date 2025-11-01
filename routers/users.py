from typing import Annotated
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound # 若 ORM 找不到資料時，引發的錯誤類
from sqlmodel import select
from db.models import get_session
from tool.tools import flash_message
from db.models.users import Users
from itsdangerous import URLSafeSerializer
from tool.authentication import create_session
import os


users = APIRouter(prefix="/users")

templates = Jinja2Templates(directory="templates")

sessionDep = Annotated[AsyncSession, Depends(get_session)]

# session storage
sessions = {}

# 初始化，用於簽名 session id
serializer = URLSafeSerializer(os.getenv("SESSION_SECRET", "default_secret"), salt=os.getenv("SALT"))

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
  request: Request,
  session: sessionDep
): 
  form = request.state.form # 讀取表單訊息
  email = form.get("email") # 讀取 email
  password = form.get("password") # 讀取 password

  result = select(Users).where(Users.email == email)
  user = await session.execute(result)

  # 檢查是否有 mail
  try :
    user = user.scalar_one()
  except NoResultFound as e:
    flash_message(request, "無此 mail，請重新輸入", "error")
    raise e
  
  # 檢查密碼輸入是否正確
  if user.password != password : 
    flash_message(request, "密碼輸入錯誤，請重新輸入", "error")
    raise Exception
  
  else :
  
    # 建立已簽章好的 session id
    signed_session_id = create_session(sessions, user, serializer)

    # 設定 Response 物件，會重導向登入頁面
    redirect = RedirectResponse("/todos/", status_code=303)

    #在 Response 中設定 set_cookie 參數，httponly 可以防止 JavaScript 存取資料
    redirect.set_cookie(key="session_id", value=signed_session_id, httponly=True)

  return redirect


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
