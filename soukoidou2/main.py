import sys
import os

# プロジェクトルート（EXE化時はその実行パス）を sys.path に追加
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# 各ディレクトリも sys.path に追加（モジュール間の直接インポートをサポート）
for d in ['mymodules', 'soukoidou', 'soukoidou2']:
    p = os.path.join(root_dir, d)
    if p not in sys.path:
        sys.path.append(p)

from soukoidou2 import app

def main()->None:
    app.soukoidou2()

if __name__ == '__main__':
    main()
