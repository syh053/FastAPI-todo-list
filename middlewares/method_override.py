from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import Response

class MethodOverrideMiddle(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next):
    if request.method == "POST":
      form = await request.form()
      method = form.get("_method") or "POST"

      request.scope["method"] = str(method).upper() # 改變 HTTP 方法
    
      request.state.form = form

    response: Response = await call_next(request)

    return response