import os
import sys
import subprocess
from pathlib import Path

# 将当前目录添加到Python路径中
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 确保上传目录存在
uploads_dir = Path("./uploads")
uploads_dir.mkdir(exist_ok=True)
print(f"确保上传目录存在: {uploads_dir.absolute()}")

# 启动应用
print("正在启动应用...")
subprocess.run(["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"], shell=True) 