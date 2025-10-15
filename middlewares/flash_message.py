from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class FlashMessageMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # 從 session 中取得 flash message
        flash = request.session.pop("_flash", None)
       
        # 將 flash message 附加到 request.state
        request.state.message = flash
        
        # 繼續處理請求
        response = await call_next(request)
        
        return response