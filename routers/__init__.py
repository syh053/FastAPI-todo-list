from fastapi import APIRouter, Request
from routers.todos import todos
from routers.users import users
from fastapi.templating import Jinja2Templates

router = APIRouter()

router.include_router(users)
router.include_router(todos)

templates = Jinja2Templates(directory="templates")

""" 初始路由 """
@router.get("/")
async def index(request: Request):
  return templates.TemplateResponse(request, 'index.html')
