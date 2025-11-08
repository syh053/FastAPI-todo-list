from fastapi import Request
from tool.authentication import analyze_session
from routers.users import sessions
from tool.message import flash_message
from tool.error import NotAuthenticatedException

  
""" 檢查是否驗證 """
async def isAuthemticated(request: Request):
   is_login = analyze_session(request, sessions)

   if not is_login :
     flash_message(request, "尚未登入", "error")
     raise NotAuthenticatedException
   
""" 儲存使用者資訊 """
async def save_user_info(request: Request):
   return request.state.user
  