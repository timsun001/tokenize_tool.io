# 导入所需模块和函数
import subprocess
import sys

def run_tool():
    # 调用 Python 脚本文件
    subprocess.call([sys.executable, 'tokenize_tool.py'])

if __name__ == '__main__':
    run_tool()