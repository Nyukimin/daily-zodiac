from __future__ import annotations

from datetime import datetime, timezone, timedelta
from pathlib import Path
import json
import os
import shutil
from typing import Dict, Any, List

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

def get_jst_date_str() -> str:
    return datetime.now(JST).strftime("%Y-%m-%d")


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

def _render_hero_html(
    data: Dict[str, Any], img_src: str, aspect_ratio: str, page_title: str
) -> str:
    """ヒーローレイアウトのHTMLを生成。index / 星座ページ共通。"""
    base = BASE_PATH.rstrip("/") + "/"
    sign = data.get("sign", "aries")

    choices_items = data.get("choices", [])[:3]
    choices_html = "\n".join([
        f'''          <a href="{base}{sign}/" class="block rounded-2xl bg-white/10 ring-1 ring-white/15 backdrop-blur-xl p-4 text-left hover:bg-white/12 transition">
            <p class="text-sm font-semibold">{c}</p>
          </a>'''
        for c in choices_items
    ]) if choices_items else ""

    other_signs_html = "\n".join([
        f'          <li><a href="{base}{s}/" class="hover:text-white">{SIGN_JA.get(s, s)}</a></li>'
        for s in SIGNS
    ])

    return f"""<!doctype html>
<html lang="ja">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <base href="{BASE_PATH}">
  <title>{page_title}</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>

<body class="min-h-screen bg-zinc-950 text-zinc-50 overflow-x-hidden">
  <!-- 背景（暗幕＋ほんの少しの光） -->
  <div class="fixed inset-0 -z-10">
    <div class="absolute inset-0 bg-zinc-950"></div>
    <div class="absolute -top-40 -left-40 h-[520px] w-[520px] rounded-full bg-fuchsia-500/15 blur-3xl"></div>
    <div class="absolute -bottom-48 -right-48 h-[620px] w-[620px] rounded-full bg-amber-400/10 blur-3xl"></div>
    <div class="absolute inset-0 bg-gradient-to-b from-zinc-950/70 via-zinc-950/55 to-zinc-950/85"></div>
  </div>

  <!-- ヒーロー全体 -->
  <main class="mx-auto max-w-6xl px-4 py-10">
    <header class="flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="h-10 w-10 rounded-2xl bg-white/10 ring-1 ring-white/15 backdrop-blur grid place-items-center">
          <span class="text-sm font-semibold">✦</span>
        </div>
        <div>
          <p class="text-xs text-zinc-200/80">占いは娯楽。結果が読みやすいことを優先。</p>
          <h1 class="text-lg font-semibold tracking-tight">今日の星座占い</h1>
        </div>
      </div>

      <div class="text-xs text-zinc-200/70">広告枠は後で差し込み</div>
    </header>

    <section class="relative mt-8 w-full rounded-[28px] ring-1 ring-white/12 bg-white/5 overflow-hidden" style="min-height:42vh;">
      <!-- 人物（右寄せ。主役は結果なので、少し引く） -->
      <div class="absolute inset-y-0 right-0 w-[32%] min-h-full hidden md:block">
        <img
          src="./{img_src}"
          alt="key visual"
          class="h-full w-full object-contain object-[65%_20%] opacity-80"
        />
        <!-- 人物側を少し沈める暗幕（文字への干渉を防ぐ） -->
        <div class="absolute inset-0 bg-gradient-to-l from-zinc-950/40 via-zinc-950/60 to-zinc-950/85"></div>
        <!-- 下側暗くしてカードを浮かせる -->
        <div class="absolute inset-0 bg-gradient-to-t from-zinc-950/35 via-transparent to-transparent"></div>
      </div>

      <!-- モバイルは人物を薄い背景にする -->
      <div class="absolute inset-0 md:hidden">
        <img
          src="./{img_src}"
          alt="key visual"
          class="h-full w-full object-contain object-[60%_15%] opacity-35 blur-[1px]"
        />
        <div class="absolute inset-0 bg-zinc-950/65"></div>
      </div>

      <!-- 左カラム（結果） -->
      <div class="relative grid gap-6 p-6 sm:p-8 md:w-[65%]">
        <div class="flex items-start justify-between gap-4">
          <div>
            <p class="text-xs text-zinc-200/80">{data["date"]} / {data["sign_ja"]}</p>
            <h2 class="mt-1 text-2xl font-semibold tracking-tight">今日の結果</h2>
          </div>
        </div>

        <!-- 要約 -->
        <div class="rounded-2xl bg-zinc-950/35 ring-1 ring-white/12 backdrop-blur-xl p-5">
          <p class="text-xs text-zinc-200/80">要約</p>
          <p class="mt-1 text-sm leading-relaxed text-zinc-50">
            {data["summary"]}
          </p>
        </div>

        <!-- 選択肢 -->
        <div class="grid gap-3 sm:grid-cols-2">
{choices_html}
        </div>

        <!-- 次の一歩 -->
        <div class="rounded-2xl bg-white/10 ring-1 ring-white/15 backdrop-blur-xl p-5 flex items-center justify-between gap-4">
          <div>
            <p class="text-xs text-zinc-200/80">次の一歩（1つだけ）</p>
            <p class="mt-1 text-sm font-semibold text-zinc-50">{data["next_step"]}</p>
          </div>
          <a href="{base}" class="shrink-0 rounded-2xl bg-white text-zinc-950 px-4 py-2 text-sm font-semibold hover:bg-zinc-100 transition">
            もう一回みる
          </a>
        </div>

        <!-- 他の星座 -->
        <p class="text-xs text-zinc-200/80">他の星座:</p>
        <ul class="sign-grid text-xs text-zinc-200/80 flex flex-wrap gap-x-2 gap-y-1">
{other_signs_html}
        </ul>

        <!-- 注意書き -->
        <p class="text-[11px] text-zinc-200/70 leading-relaxed">
          ※占いは娯楽です。医療・法律・投資などの判断材料としては使いません。
        </p>
      </div>

      <!-- 右下：広告枠（結果の邪魔をしない位置） -->
      <aside class="relative hidden md:block">
        <div class="absolute bottom-6 right-6 w-[300px] rounded-3xl bg-white/8 ring-1 ring-white/12 backdrop-blur-xl p-5">
          <p class="text-sm font-semibold">広告（プレースホルダ）</p>
          <p class="mt-2 text-xs text-zinc-200/80">結果の可読性を優先して、隅に固定。</p>
          <div class="ad-slot mt-4 h-24 rounded-2xl bg-zinc-950/35 ring-1 ring-white/10 grid place-items-center text-xs text-zinc-200/70">
            Ad Slot
          </div>
        </div>
      </aside>
    </section>
  </main>
</body>
</html>
"""


def write_sign_files(out_root: Path, sign: str, data: Dict[str, Any]) -> None:
    """星座ページ（カラー キービジュアル）を出力。"""
    sign_dir = out_root / sign
    sign_dir.mkdir(parents=True, exist_ok=True)

    (sign_dir / "index.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    img_src, _ = get_key_visual_for_sign_and_date(sign, data["date"])
    page_title = f"{data['sign_ja']} / {data['date']} - 今日の星座占い"
    html = _render_hero_html(data, img_src, "2/3", page_title)
    (sign_dir / "index.html").write_text(html, encoding="utf-8")

def write_index(out_root: Path, date_str: str, preview_data: Dict[str, Any]) -> None:
    """トップページ（RANAI キービジュアル）を出力。"""
    img_src, _ = get_key_visual_for_date(date_str)
    html = _render_hero_html(
        preview_data, img_src, "2/3", page_title="占い（結果を読むUI）"
    )
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

    templates = load_templates(Path("assets/templates.json"))

    preview_data: Dict[str, Any]
    try:
        preview_data = build_one_from_templates(templates, "aries", date_str)
    except Exception:
        preview_data = fallback_one("aries", date_str, Exception("preview"))
    write_index(out_root, date_str, preview_data)

    for sign in SIGNS:
        try:
            data = build_one_from_templates(templates, sign, date_str)
        except Exception as e:
            data = fallback_one(sign, date_str, e)
        write_sign_files(out_root, sign, data)


if __name__ == "__main__":
    generate_site()
