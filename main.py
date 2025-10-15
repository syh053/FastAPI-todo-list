from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from routers import router
from middlewares.method_override import MethodOverrideMiddle
from middlewares.flash_message import FlashMessageMiddleware
from middlewares.error_message import ErrorMessageMiddle

app = FastAPI()

# middleware，每一個 HTTP 請求進來時先進來這個 middleware，再分配要進到哪一個路由
app.add_middleware(MethodOverrideMiddle)

# 訊息處理 middleware
app.add_middleware(FlashMessageMiddleware)

# 錯誤訊息處理 middleware
app.add_middleware(ErrorMessageMiddle)

# 自動在 request 中加入 session 並簽名
app.add_middleware(SessionMiddleware, secret_key="secret")

# 總路由
app.include_router(router)
