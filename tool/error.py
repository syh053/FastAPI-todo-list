"""
自定義例外類別
"""

# 尚未登入例外類別
class NotAuthenticatedException(Exception):
  """使用者未登入"""
  def __init__(self, message: str = "尚未登入"):
    self.message = message
    super().__init__(self.message)
