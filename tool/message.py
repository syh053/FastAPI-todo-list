from fastapi import Request

""" 建立 flash_message """
def flash_message(request: Request, message:str, category:str = "info"):

  request.session["_flash"] = {"message": message, "category": category}


""" 取出 flash_message """
def get_flash_message(request: Request):

  message = request.session.pop("_flash", None)

  return message