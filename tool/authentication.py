import secrets
from fastapi import Request
from db.models.users import Users
from itsdangerous import URLSafeSerializer


""" 建立 session id """
def create_session(sessions, user: Users, serializer: URLSafeSerializer):

  # 產生 session id
  session_id = secrets.token_hex(16)

	# 將 session 寫入 session storage 中
  sessions[session_id] = {"id": user.id, "email": user.email, "name": user.name}

  # 序列化簽章
  signed_session_id = serializer.dumps(session_id)

  return signed_session_id


""" 解析 session id """
def analyze_session(request: Request, serializer: URLSafeSerializer, sessions):
	# 取得 request 中 cookie 夾帶的 session id 
  session_cookie = request.cookies.get("session_id")

	# 有 session id 時
  if session_cookie:

	  # 反序列化 session id
    analyzed_session = serializer.loads(session_cookie)

    # 從 session storage 中找出對應的資料
    user_data = sessions[analyzed_session]

    return user_data
