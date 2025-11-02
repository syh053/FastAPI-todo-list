from itsdangerous import URLSafeSerializer
import os


"""
初始化，用於簽名 session id
"""
def get_serializer():

  return URLSafeSerializer(
    os.getenv("SESSION_SECRET", "default_secret"),
    salt=os.getenv("SALT")
    )
