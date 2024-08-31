# 使用官方的 Python 3.12.4 镜像作为基础镜像
FROM python:3.12.4-slim

# 更新包管理器和安装 curl（用于后续步骤，必要时可以省略）
RUN apt-get update && apt-get install -y curl && apt-get clean && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 创建 result 目录
RUN mkdir -p /app/result

# 复制 Python 项目依赖项描述文件
COPY requirements.txt .

# 安装 Python 依赖项
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目的其余部分到容器中
COPY . .

# 暴露 FastAPI 端口
EXPOSE 8000

# 运行 FastAPI 应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

