from fastapi import FastAPI, Request
from starlette.middleware.sessions import SessionMiddleware
from routers import router

app = FastAPI()
app.include_router(router)

# 自動在 request 中加入 session 並簽名
app.add_middleware(SessionMiddleware, secret_key="secret")

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
