from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def index():
  return "Hello World!"

@app.get("/todos")
async def get_todos():
  return "get todos"

@app.get("/todos/new")
async def get_todos_new_page():
  return "get todos new page"

@app.post("/todos")
async def create_todos():
  return "add todos"

@app.get("/todos/{id}")
async def get_todos_detail(id: int):
  return f"get todo : {id}"

@app.get("/todos/{id}/edit")
async def get_todos_edit_page(id: int):
  return f"get {id} todos edit page"

@app.put("todos/{id}")
async def update_todos(id: int):
  return f"todos {id} modified"

@app.delete("/todos/{id}")
async def delete_todos(id: int):
  return f"delete {id} todos"
  