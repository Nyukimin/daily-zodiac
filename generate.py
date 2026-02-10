from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import os
from typing import Dict, Any, List

BASE_PATH = os.environ.get("BASE_PATH", "/daily-zodiac/")

JST = timezone(timedelta(hours=9))

SIGNS: List[str] = [
    "aries","taurus","gemini","cancer","leo","virgo",
    "libra","scorpio","sagittarius","capricorn","aquarius","pisces"
]

# 表示名だけ日本語にする（URLは英語スラッグのまま）
SIGN_JA: Dict[str, str] = {
    "aries": "牡羊座",
    "taurus": "牡牛座",
    "gemini": "双子座",
    "cancer": "蟹座",
    "leo": "獅子座",
    "virgo": "乙女座",
    "libra": "天秤座",
    "scorpio": "蠍座",
    "sagittarius": "射手座",
    "capricorn": "山羊座",
    "aquarius": "水瓶座",
    "pisces": "魚座",
}

def get_jst_date_str() -> str:
    return datetime.now(JST).strftime("%Y-%m-%d")


def load_templates(path: str | Path) -> dict:
    """templates.json を読み込んで返す。"""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def select_template(templates: dict, sign: str, date_str: str) -> dict:
    """日付からテンプレを選ぶ（乱数なし、同日・同星座で固定）。"""
    yyyymmdd = int(date_str.replace("-", ""))
    arr = templates[sign]
    idx = yyyymmdd % len(arr)
    return arr[idx]


def build_one_from_templates(
    templates: dict, sign: str, date_str: str
) -> Dict[str, Any]:
    """テンプレから date, sign, sign_ja を付与した dict を作る。"""
    t = select_template(templates, sign, date_str)
    ja = SIGN_JA.get(sign, sign)
    return {
        "date": date_str,
        "sign": sign,
        "sign_ja": ja,
        "summary": t["summary"],
        "choices": t["choices"],
        "next_step": t["next_step"],
    }


def build_one(sign: str, date_str: str) -> Dict[str, Any]:
    """後方互換用。テンプレから取得する。"""
    templates = load_templates(Path("assets/templates.json"))
    return build_one_from_templates(templates, sign, date_str)

def fallback_one(sign: str, date_str: str, err: Exception) -> Dict[str, Any]:
    ja = SIGN_JA.get(sign, sign)
    return {
        "date": date_str,
        "sign": sign,
        "sign_ja": ja,
        "summary": f"{ja}の今日の要約（フォールバック）",
        "choices": ["少し整える", "一歩引く", "まず確認する"],
        "next_step": "机の上を1分だけ片付ける"
    }

def render_html(data: Dict[str, Any]) -> str:
    ja = data.get("sign_ja", data["sign"])
    choices = data.get("choices", [])
    li = "\n".join([f"      <li>{c}</li>" for c in choices])

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <base href="{BASE_PATH}">
  <title>{ja} / {data["date"]} - 今日の星座占い</title>
</head>
<body>
  <p><a href="./">← 入口へ</a></p>

  <h1>{ja} / {data["date"]}</h1>
  <p>{data["summary"]}</p>

  <h2>選択肢</h2>
  <ol>
{li}
  </ol>

  <h2>次の一歩</h2>
  <p>{data["next_step"]}</p>
</body>
</html>
"""

def write_sign_files(out_root: Path, sign: str, data: Dict[str, Any]) -> None:
    sign_dir = out_root / sign
    sign_dir.mkdir(parents=True, exist_ok=True)

    (sign_dir / "index.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    (sign_dir / "index.html").write_text(
        render_html(data),
        encoding="utf-8"
    )

def write_index(out_root: Path) -> None:
    links = "\n".join([
        f'    <li><a href="./{s}/">{SIGN_JA.get(s, s)}</a></li>'
        for s in SIGNS
    ])

    html = f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <base href="{BASE_PATH}">
  <title>今日の星座占い</title>
</head>
<body>
  <h1>今日の星座占い</h1>
  <ul>
{links}
  </ul>
</body>
</html>
"""
    (out_root / "index.html").write_text(html, encoding="utf-8")


def generate_site(
    date_str: str | None = None,
    out_dir: str | Path = "site",
) -> None:
    """日次占いサイトを生成する。"""
    if date_str is None:
        date_str = get_jst_date_str()
    out_root = Path(out_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    templates = load_templates(Path("assets/templates.json"))

    write_index(out_root)

    for sign in SIGNS:
        try:
            data = build_one_from_templates(templates, sign, date_str)
        except Exception as e:
            data = fallback_one(sign, date_str, e)
        write_sign_files(out_root, sign, data)


def main() -> None:
    generate_site()


if __name__ == "__main__":
    main()
