from typing import Annotated
from fastapi import APIRouter, Request, Depends
from fastapi.responses  import RedirectResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import os
from dotenv import load_dotenv
from urllib.parse import urlencode
import httpx
from tool.message import flash_message
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import get_session
from db.models.users import Users
from sqlmodel import select
from tool.authentication import create_session
from routers.users import sessions
import string
import random
import bcrypt


load_dotenv()


oauth2 = APIRouter(prefix="/oauth2")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/oauth2/token")

sessionDep = Annotated[AsyncSession, Depends(get_session)]


@oauth2.post("/token")
async def token(form_data: OAuth2PasswordRequestForm = Depends()):
  return {
    'access_token' : form_data.username + '_token',
}

@oauth2.get('/')
async def index(token: str = Depends(oauth2_scheme)):
  return {'the_token' : token}


# Facebook OAuth 登入頁面
@oauth2.get("/facebook/login")
def facebook_login():
    params = {
        "client_id": os.getenv("FACEBOOK_CLIENT_ID"),
        "redirect_uri": os.getenv("FACEBOOK_REDIRECT_URI"),
        "scope": "email",
        "response_type": "code",
        "auth_type": "rerequest"  # 若想要求重新授權
    }
    url = "https://www.facebook.com/v17.0/dialog/oauth?" + urlencode(params)

    return RedirectResponse(url)


# Facebook OAuth callback
@oauth2.get("/facebook/callback")
async def facebook_callback(
   request: Request,
   session: sessionDep,
   code: str
   ):

    # 用 code 換 access token
    token_url = "https://graph.facebook.com/v17.0/oauth/access_token"
    params = {
        "client_id": os.getenv("FACEBOOK_CLIENT_ID"),
        "redirect_uri": os.getenv("FACEBOOK_REDIRECT_URI"),
        "client_secret": os.getenv("FACEBOOK_CLIENT_SECRET"),
        "code": code
    }

    async with httpx.AsyncClient() as client :
       res = await client.get(token_url, params=params)
       data = res.json()

    access_token = data.get("access_token")

    if not access_token:
       flash_message(request, "沒有 token", "error")
       raise Exception
    
    # 用 access token 取得使用者資訊
    user_info_url = "https://graph.facebook.com/me"
    user_params = {
        "fields": "id,name,email",
        "access_token": access_token
    }

    async with httpx.AsyncClient() as client:
        user_resp = await client.get(user_info_url, params=user_params)
        user_data = user_resp.json()

        name = user_data["name"]
        email = user_data["email"]

    statement = select(Users).where(Users.email == email)
    result = await session.execute(statement)
    user = result.scalar()

    # 若沒有此使用者就建立資料
    if not user:
      # 設定隨機密碼
      chars = string.ascii_letters + string.digits + string.punctuation
      password = "".join(random.choice(chars) for _ in range(12))
      
      hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

      session.add(Users(email=email, name=name, password=hashed_password))

      # 提交資料庫變更
      await session.commit()

      statement = select(Users).where(Users.email == email)
      result = await session.execute(statement)
      user = result.scalar()

    flash_message(request, "登入成功", "success")

    # 建立已簽章好的 session id
    signed_session_id = create_session(sessions, user)

    # 設定 Response 物件，會重導向登入頁面
    redirect = RedirectResponse("/todos/", status_code=303)

    #在 Response 中設定 set_cookie 參數，httponly 可以防止 JavaScript 存取資料
    redirect.set_cookie(key="session_id", value=signed_session_id, httponly=True)

    return redirect
