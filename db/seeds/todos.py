from pathlib import Path
import sys

package_path = str(Path().cwd().resolve() / "db")
sys.path.append(package_path)

from models import get_session
from models.todos import Todos

seed_data = [Todos(name=f"Todo {i}") for i in range(1, 11)]

session = next(get_session())

session.add_all(seed_data)
session.commit()

print("Seed 資料已經新增完成")