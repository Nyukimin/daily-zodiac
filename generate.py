"""日次で星座占いの HTML/JSON を生成するスクリプト（MVP）。"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
from typing import Dict, Any, List

JST = timezone(timedelta(hours=9))

SIGNS: List[str] = [
    "aries", "taurus", "gemini", "cancer", "leo", "virgo",
    "libra", "scorpio", "sagittarius", "capricorn", "aquarius", "pisces",
]


def get_jst_date_str() -> str:
    return datetime.now(JST).strftime("%Y-%m-%d")


def build_one(sign: str, date_str: str) -> Dict[str, Any]:
    # TODO: ここを「占い資産」や天体計算結果に置換する
    return {
        "date": date_str,
        "sign": sign,
        "summary": f"{sign} の今日の要約（ダミー）",
        "choices": ["少し整える", "一歩引く", "まず確認する"],
        "next_step": "机の上を1分だけ片付ける",
    }


def fallback_one(sign: str, date_str: str, err: Exception) -> Dict[str, Any]:
    return {
        "date": date_str,
        "sign": sign,
        "summary": f"{sign} の今日の要約（フォールバック）",
        "choices": ["少し整える", "一歩引く", "まず確認する"],
        "next_step": "机の上を1分だけ片付ける",
    }


def render_html(data: Dict[str, Any]) -> str:
    choices = data.get("choices", [])
    li = "\n".join([f"  <li>{c}</li>" for c in choices])
    return f"""<h1>{data["sign"]} / {data["date"]}</h1>
<p>{data["summary"]}</p>
<h2>選択肢</h2>
<ol>
{li}
</ol>
<h2>次の一歩</h2>
<p>{data["next_step"]}</p>
"""


def write_sign_files(out_root: Path, sign: str, data: Dict[str, Any]) -> None:
    sign_dir = out_root / sign
    sign_dir.mkdir(parents=True, exist_ok=True)

    (sign_dir / "index.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (sign_dir / "index.html").write_text(
        render_html(data),
        encoding="utf-8",
    )


def write_index(out_root: Path) -> None:
    links = "\n".join([f'<li><a href="/{s}/">{s}</a></li>' for s in SIGNS])
    html = f"""<h1>今日の星座占い</h1>
<ul>
{links}
</ul>
"""
    (out_root / "index.html").write_text(html, encoding="utf-8")


def main() -> None:
    date_str = get_jst_date_str()
    out_root = Path("site")
    out_root.mkdir(parents=True, exist_ok=True)

    write_index(out_root)

    for sign in SIGNS:
        try:
            data = build_one(sign, date_str)
        except Exception as e:
            data = fallback_one(sign, date_str, e)
        write_sign_files(out_root, sign, data)


if __name__ == "__main__":
    main()
