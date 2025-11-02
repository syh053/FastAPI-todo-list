import secrets
from fastapi import Request
from db.models.users import Users
from tool.serializer import get_serializer


""" 建立 session id """
def create_session(sessions, user: Users):
  # 取得序列化方法
  serializer = get_serializer()

  # 產生 session id
  session_id = secrets.token_hex(16)

	# 將 session 寫入 session storage 中
  sessions[session_id] = {"id": user.id, "email": user.email, "name": user.name}

  # 序列化簽章
  signed_session_id = serializer.dumps(session_id)

  return signed_session_id


""" 解析 session id """
def analyze_session(request: Request, sessions: dict):
	# 取得 request 中 cookie 夾帶的 session id 
  session_cookie = request.cookies.get("session_id")

	# 有 session id 時
  if session_cookie:

    # 取得序列化方法
    serializer = get_serializer()

	  # 反序列化 session id
    analyzed_session = serializer.loads(session_cookie)

    # 從 session storage 中找出對應的資料
    user_data = sessions.get(analyzed_session)

    # 確認 user_data 是否有值
    if not user_data :
      return False
    
    else :
      request.state.user = user_data

      return True
  
  else :
    return False
