# 使用官方Python映像檔作為基礎
FROM python:3.11-slim

# 在容器內部設置工作目錄
WORKDIR /app

# 將應用程式所需的套件安裝到容器中
COPY requirement.txt .

# 透過pip安裝需求套件
RUN pip install -r requirement.txt

# 將本機當前工作目錄複製到容器當前工作目錄
COPY . .

# 啟動應用程式
CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "5555"]