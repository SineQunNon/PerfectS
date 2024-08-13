import sys
import os

# 현재 프로젝트의 루트 디렉토리를 PYTHONPATH에 추가
def config():
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))