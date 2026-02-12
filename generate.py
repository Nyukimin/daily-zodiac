from __future__ import annotations

import hashlib
import json
import os
import shutil
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader, select_autoescape

load_dotenv()

# デプロイ時（GitHub Actions）は /daily-zodiac/、ローカルは /
_base = os.environ.get("BASE_PATH")
if _base is None:
    _base = "/daily-zodiac/" if os.environ.get("GITHUB_ACTIONS") else "/"
BASE_PATH = _base if _base.endswith("/") else _base + "/"

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


def stable_hash_to_int(text: str) -> int:
    """Pythonのhash()はランダム化されるため禁止。sha256で安定化してint化。"""
    h = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def pick_index(date_key: str, key: str, n: int) -> int:
    """決定論的インデックス選択。stable_hash_to_int(date_key + ":" + key) % n"""
    return stable_hash_to_int(date_key + ":" + key) % n


def get_now_jst() -> datetime:
    """JSTの現在時刻を返す。"""
    return datetime.now(JST)


def get_date_key_jst(now_jst: datetime | None = None) -> str:
    """JST日付キー YYYY-MM-DD を返す。"""
    if now_jst is None:
        now_jst = get_now_jst()
    return now_jst.strftime("%Y-%m-%d")


def get_jst_date_str() -> str:
    """後方互換用。get_date_key_jst(get_now_jst()) と同等。"""
    return get_date_key_jst()


def _get_png_aspect_ratio(path: Path) -> tuple[int, int] | None:
    """PNG の IHDR から幅・高さを読む。"""
    try:
        with open(path, "rb") as f:
            data = f.read(24)
        if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n":
            w = int.from_bytes(data[16:20], "big")
            h = int.from_bytes(data[20:24], "big")
            return (w, h) if w > 0 and h > 0 else None
    except (OSError, ValueError):
        pass
    return None


def _load_color_images() -> List[tuple[str, List[Path]]]:
    """assets/images/カラー を走査し [(色名, [png_path, ...]), ...] を返す。PNGのみ。"""
    color_root = Path("assets/images/カラー")
    if not color_root.exists():
        return []
    result: List[tuple[str, List[Path]]] = []
    for color_dir in sorted(color_root.iterdir()):
        if not color_dir.is_dir():
            continue
        pngs = sorted(color_dir.glob("*.png"))
        if pngs:
            result.append((color_dir.name, pngs))
    return result


_COLOR_IMAGES_CACHE: List[tuple[str, List[Path]]] | None = None


def _get_color_images() -> List[tuple[str, List[Path]]]:
    """_load_color_images の結果をキャッシュして返す。"""
    global _COLOR_IMAGES_CACHE
    if _COLOR_IMAGES_CACHE is None:
        _COLOR_IMAGES_CACHE = _load_color_images()
    return _COLOR_IMAGES_CACHE


def get_key_visual_for_sign_and_date(sign: str, date_str: str) -> tuple[str, str]:
    """星座・日付に応じて カラー からキービジュアルを選ぶ。(path, aspect_ratio_css)
    同一日に同色重複なし、連続日同星座同色なし、均等利用、色内ループを満たす。
    """
    colors = _get_color_images()
    default = ("images/RANAI/RANAI_01.png", "2/3")
    if len(colors) < 12:
        return default
    try:
        sign_idx = SIGNS.index(sign)
    except ValueError:
        return default
    yyyymmdd = int(date_str.replace("-", ""))
    num_colors = len(colors)
    color_idx = (yyyymmdd + sign_idx) % num_colors
    color_name, images = colors[color_idx]
    image_idx = (yyyymmdd * num_colors + sign_idx) % len(images)
    chosen = images[image_idx]
    path = f"images/カラー/{color_name}/{chosen.name}".replace("\\", "/")
    dims = _get_png_aspect_ratio(chosen)
    ratio = f"{dims[0]}/{dims[1]}" if dims else "2/3"
    return (path, ratio)


def get_key_visual_for_date(date_str: str) -> tuple[str, str]:
    """日付に応じてキービジュアルを順に選ぶ。トップページ用（RANAI）。(path, aspect_ratio_css)"""
    ranai_dir = Path("assets/images/RANAI")
    default = ("images/RANAI/RANAI_01.png", "2/3")
    if not ranai_dir.exists():
        return default
    files = sorted(ranai_dir.glob("RANAI_*.png"))
    if not files:
        return default
    yyyymmdd = int(date_str.replace("-", ""))
    idx = yyyymmdd % len(files)
    chosen = files[idx]
    path = f"images/RANAI/{chosen.name}"
    dims = _get_png_aspect_ratio(chosen)
    ratio = f"{dims[0]}/{dims[1]}" if dims else "2/3"
    return (path, ratio)


def load_patterns() -> Dict[str, Any]:
    """fallback/global_patterns.json と fallback/sign_patterns.json を読む。"""
    result: Dict[str, Any] = {}
    global_path = Path("fallback/global_patterns.json")
    sign_path = Path("fallback/sign_patterns.json")
    if global_path.exists():
        with open(global_path, encoding="utf-8") as f:
            result["global"] = json.load(f)
    else:
        result["global"] = {"patterns": []}
    if sign_path.exists():
        with open(sign_path, encoding="utf-8") as f:
            result["signs"] = json.load(f)
    else:
        result["signs"] = {}
    return result


def build_global_fallback(date_key: str) -> Dict[str, Any]:
    """日付キーから global ブロックをフォールバックで生成。"""
    patterns = load_patterns()
    arr = patterns.get("global", {}).get("patterns", [])
    if not arr:
        return {
            "summary": "今日は整えるほど前に進みやすい日。焦りは小さく切って扱うと安定する。",
            "advice": "作業前に机の上を3分だけ整える"
        }
    idx = pick_index(date_key, "global", len(arr))
    return arr[idx]


def build_sign_fallback(date_key: str, sign_key: str) -> Dict[str, Any]:
    """日付・星座からフォールバックで {summary, advice} を生成。"""
    patterns = load_patterns()
    sign_patterns = patterns.get("signs", {}).get(sign_key, [])
    if not sign_patterns:
        ja = SIGN_JA.get(sign_key, sign_key)
        return {
            "summary": f"{ja}の今日の要約（フォールバック）",
            "advice": "机の上を1分だけ片付ける"
        }
    idx = pick_index(date_key, "sign:" + sign_key, len(sign_patterns))
    return sign_patterns[idx]


def try_build_from_engine(
    date_key: str,
    llm_scope: str | None = None,
) -> tuple[Dict[str, Any], Dict[str, Dict[str, Any]]]:
    """占星術エンジン（flatlib）+ Gemini で生成。失敗時は raise してフォールバックへ。

    llm_scope: "global" のとき全体運のみ LLM で生成、星座はフォールバック（テスト用）。
    None または "all" で従来どおり全13回 LLM 呼び出し。
    """
    from astro.engine import get_chart_data
    from astro.llm_formatter import format_with_llm

    if llm_scope is None:
        llm_scope = os.environ.get("LLM_SCOPE", "all")

    astro_data = get_chart_data(date_key)
    global_block = format_with_llm(astro_data, "global")
    if global_block is None:
        raise RuntimeError("LLM format failed for global")
    time.sleep(1)  # レート制限対策

    signs_block: Dict[str, Dict[str, Any]] = {}
    if llm_scope == "global":
        for sign in SIGNS:
            signs_block[sign] = build_sign_fallback(date_key, sign)
    else:
        for sign in SIGNS:
            sign_ja = SIGN_JA.get(sign, sign)
            block = format_with_llm(astro_data, sign, sign_ja)
            if block is None:
                raise RuntimeError(f"LLM format failed for {sign}")
            signs_block[sign] = block
            time.sleep(1)  # レート制限対策
    return (global_block, signs_block)


def build_daily_payload(
    date_key: str,
    generated_at_jst_iso: str,
    llm_scope: str | None = None,
) -> Dict[str, Any]:
    """日付キーから1日分のpayload（global + signs）を組む。エンジン失敗時はフォールバック。"""
    global_block: Dict[str, Any]
    signs_block: Dict[str, Dict[str, Any]] = {}
    try:
        global_block, signs_block = try_build_from_engine(date_key, llm_scope)
    except Exception:
        global_block = build_global_fallback(date_key)
        for sign in SIGNS:
            signs_block[sign] = build_sign_fallback(date_key, sign)
    for sign in SIGNS:
        if sign not in signs_block:
            signs_block[sign] = build_sign_fallback(date_key, sign)
    return {
        "date": date_key,
        "generated_at_jst": generated_at_jst_iso,
        "global": global_block,
        "signs": signs_block,
    }


_JINJA_ENV: Environment | None = None


def _get_jinja_env() -> Environment:
    """Jinja2 環境を取得（テンプレートディレクトリは templates/）。"""
    global _JINJA_ENV
    if _JINJA_ENV is None:
        _JINJA_ENV = Environment(
            loader=FileSystemLoader("templates"),
            autoescape=select_autoescape(disabled_extensions=("html",)),
        )
    return _JINJA_ENV


def render_html_index(data: Dict[str, Any], img_src: str, base_path: str) -> str:
    """トップページ用 HTML をレンダリング。"""
    env = _get_jinja_env()
    tmpl = env.get_template("index.html")
    base_href = base_path.rstrip("/") + "/"
    signs = [(s, SIGN_JA.get(s, s)) for s in SIGNS]
    return tmpl.render(
        base_path=base_path,
        page_title="占い（結果を読むUI）",
        img_src=img_src,
        data=data,
        base_href=base_href,
        signs=signs,
        is_home=True,
    )


def render_html_sign(data: Dict[str, Any], img_src: str, base_path: str) -> str:
    """星座ページ用 HTML をレンダリング。"""
    env = _get_jinja_env()
    tmpl = env.get_template("sign.html")
    base_href = base_path.rstrip("/") + "/"
    signs = [(s, SIGN_JA.get(s, s)) for s in SIGNS]
    page_title = f"{data['sign_ja']} / {data['date']} - 今日の星座占い"
    return tmpl.render(
        base_path=base_path,
        page_title=page_title,
        img_src=img_src,
        data=data,
        base_href=base_href,
        signs=signs,
        is_home=False,
    )


def write_sign_files(out_root: Path, sign: str, data: Dict[str, Any]) -> None:
    """星座ページ（カラー キービジュアル）を出力。HTML のみ（JSON は site/data/ に統一）。"""
    sign_dir = out_root / sign
    sign_dir.mkdir(parents=True, exist_ok=True)

    img_src, _ = get_key_visual_for_sign_and_date(sign, data["date"])
    html = render_html_sign(data, img_src, BASE_PATH)
    (sign_dir / "index.html").write_text(html, encoding="utf-8")

def write_index(out_root: Path, date_str: str, preview_data: Dict[str, Any]) -> None:
    """トップページ（RANAI キービジュアル）を出力。"""
    img_src, _ = get_key_visual_for_date(date_str)
    html = render_html_index(preview_data, img_src, BASE_PATH)
    (out_root / "index.html").write_text(html, encoding="utf-8")


def write_json(payload: Dict[str, Any], path: Path) -> None:
    """payload を JSON で path に書き出す。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_site(
    date_str: str | None = None,
    out_dir: str | Path = "site",
    llm_scope: str | None = None,
) -> None:
    """日次占いサイトを生成する。

    llm_scope: "global" のとき全体運のみ LLM、星座はフォールバック（LLM_SCOPE 環境変数でも指定可）。
    """
    now = get_now_jst()
    date_key = date_str if date_str is not None else get_date_key_jst(now)
    generated_at = now.isoformat()
    scope = llm_scope if llm_scope is not None else os.environ.get("LLM_SCOPE")

    out_root = Path(out_dir)
    out_root.mkdir(parents=True, exist_ok=True)

    payload = build_daily_payload(date_key, generated_at, scope)

    (out_root / "data").mkdir(parents=True, exist_ok=True)
    write_json(payload, out_root / "data" / f"{date_key}.json")

    # 画像を site/images/ にコピー
    src_images = Path("assets/images")
    dst_images = out_root / "images"
    if src_images.exists():
        if dst_images.exists():
            shutil.rmtree(dst_images)
        shutil.copytree(
            src_images, dst_images,
            ignore=shutil.ignore_patterns("*.txt", "*.mp4")
        )

    preview_data: Dict[str, Any] = {
        "date": date_key,
        "sign": "aries",
        "sign_ja": SIGN_JA["aries"],
        "summary": payload["global"]["summary"],
        "advice": payload["global"]["advice"],
    }
    write_index(out_root, date_key, preview_data)

    for sign in SIGNS:
        s = payload["signs"][sign]
        data: Dict[str, Any] = {
            "date": date_key,
            "sign": sign,
            "sign_ja": SIGN_JA.get(sign, sign),
            "summary": s["summary"],
            "advice": s["advice"],
        }
        write_sign_files(out_root, sign, data)


if __name__ == "__main__":
    generate_site()
