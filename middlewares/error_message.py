from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from starlette.responses import Response
from fastapi.responses import RedirectResponse
from sqlalchemy.exc import NoResultFound # 若 ORM 找不到資料時，引發的錯誤類
from tool.error import NotAuthenticatedException

class ErrorMessageMiddle(BaseHTTPMiddleware):
  async def dispatch(self, request: Request, call_next) -> Response:

    try :
      response = await call_next(request)

      return response
    
    except NoResultFound as e :
      print(e)

      prev_url = request.headers.get("referer") or "/todos/"

      return RedirectResponse(prev_url, status_code=303)
    
    except NotAuthenticatedException as e:
      print(e)

      return RedirectResponse("/users/login", status_code=303)

    except Exception as e:
      print(e)

      prev_url = request.headers.get("referer") or "/todos/"

      return RedirectResponse(prev_url, status_code=303)
