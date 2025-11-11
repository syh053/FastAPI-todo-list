import asyncio # 非同步程式執行框架
from pathlib import Path
import sys

package_path = str(Path().cwd().resolve() / "db")
sys.path.append(package_path)

from models import get_session, asyne_engine # 加入非同步 engine
from models.users import Users
from models.todos import Todos
import random


async def main():
    async for session in get_session():
        try :
            """ 建立 users 種子資料 """
            users = [Users(email=f"test{i}@example.com", password="123") for i in range(1, 4)]
            session.add_all(users)

            # flush() 用來提前同步變更到資料，尚未 commit，遇到錯誤仍可 rollback
            await session.flush()

            """ 建立 todos 種子資料 """
            todos = []
    
            for i in range(1, 61):
                random_user = random.choice(users)
                todos.append(Todos(name=f"Todo {i}", user_id=random_user.id))

            session.add_all(todos)

            """ 全部成功才 commit """
            await session.commit()

        except Exception as e:
            await session.rollback()
            print(e)

    # 關閉引擎
    await asyne_engine.dispose()

    print("Seed 資料已經新增完成")




if __name__ == "__main__":
    asyncio.run(main())
