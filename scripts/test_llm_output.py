"""LLM の占い結果テスト。日時・星座をランダムに変えて実行。"""

import random
import sys
from datetime import timedelta
from pathlib import Path

# PowerShell 等での文字化け対策
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from astro.llm_formatter import format_with_llm, _get_api_key
from generate import SIGNS, SIGN_JA


def random_date() -> str:
    """ランダムな日付（2024〜2027年）を YYYY-MM-DD で返す。"""
    from datetime import datetime
    start = datetime(2024, 1, 1)
    end = datetime(2027, 12, 31)
    delta = (end - start).days
    rd = start + timedelta(days=random.randint(0, delta))
    return rd.strftime("%Y-%m-%d")


def random_signs() -> dict:
    """ランダムな惑星配置を返す。"""
    planets = {}
    for key in ["sun", "moon", "mercury", "venus", "mars", "jupiter", "saturn"]:
        planets[key] = random.choice(SIGNS)
    return planets


def random_moon_phase() -> str:
    """ランダムな月相を返す。"""
    phases = [
        "New Moon", "Waxing Crescent", "First Quarter", "Waxing Gibbous",
        "Full Moon", "Waning Gibbous", "Last Quarter", "Waning Crescent",
    ]
    return random.choice(phases)


def main():
    api_key = _get_api_key()
    if not api_key:
        print("[NG] LLM_API_KEY または GEMINI_API_KEY が設定されていません")
        print("     .env に LLM_API_KEY=... を設定してください")
        return 1

    # 毎回ランダムに日付・星座を変更
    date_key = random_date()
    planets = random_signs()
    moon_phase = random_moon_phase()

    astro_data = {
        "date": date_key,
        "sun_sign": planets.get("sun", "aquarius"),
        "moon_sign": planets.get("moon", "pisces"),
        "planets": planets,
        "moon_phase": moon_phase,
    }

    sign_slug = random.choice(SIGNS)
    sign_ja = SIGN_JA.get(sign_slug, sign_slug)

    print("=" * 60)
    print("LLM 占い結果テスト（日時・星座はテストごとにランダム）")
    print("=" * 60)
    print(f"\n【入力】日付: {date_key}")
    print(f"  太陽: {astro_data['sun_sign']}, 月: {astro_data['moon_sign']}")
    print(f"  月相: {moon_phase}")
    print(f"  惑星: {planets}")
    print()

    # 全体運
    print("【1】全体運を生成中...")
    result_global = format_with_llm(astro_data, "global")
    if result_global:
        print("\n  ■ 全体運の出力")
        print(f"  要約: {result_global['summary']}")
        print(f"  アドバイス: {result_global['advice']}")
    else:
        print("  [NG] 全体運の取得に失敗しました")

    print()

    # 星座別（ランダムに1つ）
    print(f"【2】{sign_ja}（{sign_slug}）の占いを生成中...")
    result_sign = format_with_llm(astro_data, sign_slug, sign_ja)
    if result_sign:
        print(f"\n  ■ {sign_ja} の出力")
        print(f"  要約: {result_sign['summary']}")
        print(f"  アドバイス: {result_sign['advice']}")
    else:
        print(f"  [NG] {sign_ja} の取得に失敗しました")

    print("\n" + "=" * 60)
    print("テスト完了")
    print("=" * 60)

    # 結果をファイルにも保存（文字化け対策）
    out_path = Path(__file__).resolve().parent.parent / "docs" / "作業メモ" / "llm_test_output.txt"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("LLM 占い結果テスト（日時・星座はランダム）\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"日付: {date_key}\n")
        f.write(f"太陽: {astro_data['sun_sign']}, 月: {astro_data['moon_sign']}\n")
        f.write(f"月相: {moon_phase}\n")
        f.write(f"惑星: {planets}\n\n")
        if result_global:
            f.write("【全体運】\n")
            f.write(f"要約: {result_global['summary']}\n")
            f.write(f"アドバイス: {result_global['advice']}\n\n")
        if result_sign:
            f.write(f"【{sign_ja}】\n")
            f.write(f"要約: {result_sign['summary']}\n")
            f.write(f"アドバイス: {result_sign['advice']}\n")
    print(f"\n結果を保存: {out_path}")

    return 0


if __name__ == "__main__":
    exit(main())
