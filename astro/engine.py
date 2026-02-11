"""flatlib を用いたチャートデータ取得。"""

from __future__ import annotations

from typing import Any, Dict

# flatlib は pyswisseph (swisseph) に依存。Windows ではビルドが難しい場合がある。
# ImportError 時は try_build_from_engine が失敗し、フォールバックが使われる。
try:
    from flatlib.chart import Chart
    from flatlib.datetime import Datetime
    from flatlib.geopos import GeoPos
    from flatlib import const

    _FLATLIB_AVAILABLE = True
except ImportError:
    _FLATLIB_AVAILABLE = False

# flatlib の sign 名（Pisces 等）→ スラッグ（pisces）マッピング
_SIGN_TO_SLUG = {
    "Aries": "aries",
    "Taurus": "taurus",
    "Gemini": "gemini",
    "Cancer": "cancer",
    "Leo": "leo",
    "Virgo": "virgo",
    "Libra": "libra",
    "Scorpio": "scorpio",
    "Sagittarius": "sagittarius",
    "Capricorn": "capricorn",
    "Aquarius": "aquarius",
    "Pisces": "pisces",
}


def get_chart_data(date_key: str) -> Dict[str, Any]:
    """JST 正午（東京）のチャートを計算し、惑星配置・サイン等を辞書で返す。

    Args:
        date_key: YYYY-MM-DD 形式の日付文字列

    Returns:
        {"date", "sun_sign", "moon_sign", "planets", "moon_phase", ...}

    Raises:
        RuntimeError: flatlib が利用できない場合
    """
    if not _FLATLIB_AVAILABLE:
        raise RuntimeError("flatlib not available; use fallback.")

    # date_key: "2026-02-11" → flatlib Datetime: "2026/02/11"
    date_str = date_key.replace("-", "/")
    dt = Datetime(date_str, "12:00", "+09:00")
    pos = GeoPos(35.6762, 139.6503)  # 東京
    chart = Chart(dt, pos)

    planets_data: Dict[str, str] = {}
    planet_ids = [
        (const.SUN, "sun"),
        (const.MOON, "moon"),
        (const.MERCURY, "mercury"),
        (const.VENUS, "venus"),
        (const.MARS, "mars"),
        (const.JUPITER, "jupiter"),
        (const.SATURN, "saturn"),
    ]
    for pid, key in planet_ids:
        try:
            obj = chart.get(pid)
            sign = getattr(obj, "sign", None)
            if sign and sign in _SIGN_TO_SLUG:
                planets_data[key] = _SIGN_TO_SLUG[sign]
        except (AttributeError, KeyError, TypeError):
            pass

    moon_phase = ""
    try:
        moon_phase = chart.getMoonPhase()
    except (AttributeError, TypeError):
        pass

    return {
        "date": date_key,
        "sun_sign": planets_data.get("sun", ""),
        "moon_sign": planets_data.get("moon", ""),
        "planets": planets_data,
        "moon_phase": moon_phase,
    }
