"""LLM（Gemini）が正しく動作するか確認するスクリプト。"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from astro.llm_formatter import format_with_llm, _get_api_key

def main():
    api_key = _get_api_key()
    if not api_key:
        print("[NG] LLM_API_KEY または GEMINI_API_KEY が設定されていません")
        return 1

    print("[OK] API キーが設定されています")
    print("  Gemini で占い文章を生成中...")

    # ダミーの占星術データ（flatlib なしでも LLM 部分だけテスト）
    astro_data = {
        "date": "2026-02-11",
        "sun_sign": "aquarius",
        "moon_sign": "pisces",
        "planets": {"sun": "aquarius", "moon": "pisces", "mercury": "aquarius"},
        "moon_phase": "Waxing Gibbous",
    }

    result = format_with_llm(astro_data, "global")
    if result is None:
        print("[NG] LLM からの応答が取得できませんでした（API キーまたは接続を確認）")
        return 1

    print("\n[OK] LLM が正常に動作しました\n")
    print("【全体運のサンプル出力】")
    print(f"  要約: {result['summary']}")
    print(f"  選択肢: {result['choices']}")
    print(f"  次の一歩: {result['next_step']}")
    return 0


if __name__ == "__main__":
    exit(main())
