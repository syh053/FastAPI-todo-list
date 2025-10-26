from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")

users = APIRouter(prefix="/users")

@users.get("/login")
async def login_page(
  request: Request
):
  return templates.TemplateResponse("login.html", {"request" : request})


@users.get("/register")
async def register_page(
  request: Request
):
  return templates.TemplateResponse("register.html", {"request": request})


@users.post("/login")
async def login(
  request: Request
): 
  form = request.state.form # 讀取表單訊息
  email = form.get("email") # 讀取 email
  password = form.get("password") # 讀取 password

  print(email)
  print(password)

  return RedirectResponse("/todos/", status_code=303)


@users.post("/register")
async def register():
  return RedirectResponse("/users/login", status_code=303)


@users.post("/logout")
async def logout():
  return RedirectResponse("/users/login", status_code=303)
