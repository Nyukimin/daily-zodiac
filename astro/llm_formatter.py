"""Gemini Lite を用いた占い文章成形。"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any, Dict

# 環境変数 LLM_API_KEY または GEMINI_API_KEY を使用。未設定時は None を返す。

# 人格設定ファイルのパス（プロジェクトルート基準）
_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "llm_personality.yaml"

_DEFAULT_SYSTEM_INSTRUCTION = (
    "あなたは占いの文章を書くアシスタントです。"
    "娯楽として優しく、煽らず、断定を避けるトーンで書いてください。"
    "必ず次の JSON 形式のみで応答してください（他に説明は不要）: "
    '{"summary":"要約1文","advice":"アドバイス1文"}'
)

def _get_api_key() -> str | None:
    """API キーを環境変数から取得。ログにはキー値を出さない。"""
    return os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY")


def _load_personality_config() -> Dict[str, Any] | None:
    """config/llm_personality.yaml を読み込み、パースして返す。失敗時は None。"""
    if not _CONFIG_PATH.exists():
        return None
    try:
        import yaml
        with open(_CONFIG_PATH, encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception:
        return None


def _build_system_instruction() -> str:
    """人格設定から system_instruction を組み立てる。ファイル未存在時はデフォルト。"""
    config = _load_personality_config()
    if not config:
        return _DEFAULT_SYSTEM_INSTRUCTION

    parts: list[str] = []

    role = config.get("role")
    if role:
        parts.append(f"あなたは{role}です。")

    tone = config.get("tone")
    if tone and isinstance(tone, list):
        tone_str = "、".join(str(t) for t in tone)
        parts.append(f"{tone_str}トーンで書いてください。")

    avoid = config.get("avoid")
    if avoid and isinstance(avoid, list):
        avoid_str = "、".join(str(a) for a in avoid)
        parts.append(f"以下を避けてください: {avoid_str}。")

    output = config.get("output", {})
    if isinstance(output, dict):
        schema = output.get("schema")
        strict = output.get("strict", True)
        if schema and isinstance(schema, dict):
            json_example = json.dumps(schema, ensure_ascii=False)
            if strict:
                parts.append(f"必ず次の JSON 形式のみで応答してください（他に説明は不要）: {json_example}")
            else:
                parts.append(f"次の JSON 形式で応答してください: {json_example}")

    if not parts:
        return _DEFAULT_SYSTEM_INSTRUCTION
    return "".join(parts)


def format_with_llm(
    astro_data: Dict[str, Any],
    scope: str,
    sign_ja: str | None = None,
) -> Dict[str, Any] | None:
    """占星術データを Gemini で文章成形し、{summary, advice} を返す。

    Args:
        astro_data: get_chart_data() の戻り値
        scope: "global" または星座スラッグ（例: "aries"）
        sign_ja: scope が星座の場合の日本語名（例: "牡羊座"）

    Returns:
        {"summary": str, "advice": str} または None
    """
    api_key = _get_api_key()
    if not api_key:
        return None

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        return None

    if scope == "global":
        prompt = _build_global_prompt(astro_data)
    else:
        prompt = _build_sign_prompt(astro_data, scope, sign_ja or scope)

    system_instruction = _build_system_instruction()

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0,
            ),
        )
        text = getattr(response, "text", None) or str(response)
        if not text:
            return None

        # JSON を抽出（```json ... ``` やマークダウンを除去）
        parsed = _parse_json_response(text)
        if parsed and "summary" in parsed and "advice" in parsed:
            return {
                "summary": str(parsed["summary"]),
                "advice": str(parsed["advice"]),
            }
    except Exception:
        return None

    return None


def _build_global_prompt(astro_data: Dict[str, Any]) -> str:
    """全体運用のプロンプトを生成。"""
    date = astro_data.get("date", "")
    sun = astro_data.get("sun_sign", "")
    moon = astro_data.get("moon_sign", "")
    planets = astro_data.get("planets", {})
    moon_phase = astro_data.get("moon_phase", "")

    return f"""今日（{date}）の天体配置です。
太陽: {sun}、月: {moon}、月相: {moon_phase}
惑星: {json.dumps(planets, ensure_ascii=False)}

この日の全体の雰囲気・エネルギーに基づいて、今日の占い（要約・アドバイス）を JSON で出力してください。"""


def _build_sign_prompt(
    astro_data: Dict[str, Any],
    sign: str,
    sign_ja: str,
) -> str:
    """星座別のプロンプトを生成。"""
    date = astro_data.get("date", "")
    sun = astro_data.get("sun_sign", "")
    moon = astro_data.get("moon_sign", "")
    planets = astro_data.get("planets", {})
    moon_phase = astro_data.get("moon_phase", "")

    return f"""今日（{date}）の天体配置です。
太陽: {sun}、月: {moon}、月相: {moon_phase}
惑星: {json.dumps(planets, ensure_ascii=False)}

{sign_ja}（太陽が{sign}にある人）向けの今日の占い（要約・アドバイス）を、上記の天体配置を踏まえて JSON で出力してください。"""


def _parse_json_response(text: str) -> Dict[str, Any] | None:
    """レスポンスから JSON を抽出してパース。"""
    text = text.strip()
    # ```json ... ``` を探す
    m = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
    if m:
        text = m.group(1).strip()
    # { ... } を探す
    m = re.search(r"\{[\s\S]*\}", text)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
