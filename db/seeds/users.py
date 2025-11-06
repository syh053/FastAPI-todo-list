from pathlib import Path
import sys

package_path = str(Path().cwd().resolve() / "db")
sys.path.append(package_path)

import asyncio
from models import get_session, asyne_engine
from models.users import Users

users = [Users(email=f"test{i}@example.com", password="123") for i in range(1, 4)]

async def main():
  async for session in get_session():
    session.add_all(users)
    await session.commit()

    # 關閉引擎
    await asyne_engine.dispose()

    print("Seed 資料已經新增完成")

if __name__ == "__main__":
  asyncio.run(main())
