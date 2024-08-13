import sys
import os

# 현재 프로젝트의 루트 디렉토리를 PYTHONPATH에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from loader.main import loader_function

print(loader_function())