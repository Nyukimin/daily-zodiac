"""pytest 設定。プロジェクトルートを Python パスに追加。"""
import os
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

# テスト時は全体運のみ LLM 呼び出し、星座はフォールバック（品質確認しつつ高速化）
os.environ.setdefault("LLM_SCOPE", "global")
