import asyncio # 非同步程式執行框架
from pathlib import Path
import sys

package_path = str(Path().cwd().resolve() / "db")
sys.path.append(package_path)

from models import get_session, asyne_engine # 加入非同步 engine
from models.todos import Todos

seed_data = [Todos(name=f"Todo {i}") for i in range(1, 11)]

async def main():
    async for session in get_session():
        session.add_all(seed_data)
        await session.commit()
        await session.close()

    # 關閉引擎
    await asyne_engine.dispose()

    print("Seed 資料已經新增完成")


if __name__ == "__main__":
    asyncio.run(main())
