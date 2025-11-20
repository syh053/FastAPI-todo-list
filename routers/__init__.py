from fastapi import APIRouter, Request
from routers.todos import todos
from routers.users import users
from routers.oauth import oauth2
from fastapi.templating import Jinja2Templates

router = APIRouter()

router.include_router(users, tags=["註冊&登入"])
router.include_router(oauth2, tags=["OAuth2 登入"])
router.include_router(todos, tags=["todos"])

templates = Jinja2Templates(directory="templates")

""" 初始路由 """
@router.get("/")
async def index(request: Request):
  return templates.TemplateResponse(request, 'index.html')
