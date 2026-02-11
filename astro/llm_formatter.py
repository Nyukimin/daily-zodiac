"""Gemini Lite を用いた占い文章成形。"""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Dict

# 環境変数 LLM_API_KEY または GEMINI_API_KEY を使用。未設定時は None を返す。

def _get_api_key() -> str | None:
    """API キーを環境変数から取得。ログにはキー値を出さない。"""
    return os.environ.get("LLM_API_KEY") or os.environ.get("GEMINI_API_KEY")


def format_with_llm(
    astro_data: Dict[str, Any],
    scope: str,
    sign_ja: str | None = None,
) -> Dict[str, Any] | None:
    """占星術データを Gemini で文章成形し、{summary, choices, next_step} を返す。

    Args:
        astro_data: get_chart_data() の戻り値
        scope: "global" または星座スラッグ（例: "aries"）
        sign_ja: scope が星座の場合の日本語名（例: "牡羊座"）

    Returns:
        {"summary": str, "choices": [str, str, str], "next_step": str} または None
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

    system_instruction = (
        "あなたは占いの文章を書くアシスタントです。"
        "娯楽として優しく、煽らず、断定を避けるトーンで書いてください。"
        "必ず次の JSON 形式のみで応答してください（他に説明は不要）: "
        '{"summary":"要約1文","choices":["選択肢1","選択肢2","選択肢3"],"next_step":"次の一歩1文"}'
    )

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
        if parsed and "summary" in parsed and "choices" in parsed and "next_step" in parsed:
            choices = parsed["choices"]
            if not isinstance(choices, list):
                choices = [str(c) for c in (choices if isinstance(choices, (list, tuple)) else [choices])]
            if len(choices) < 3:
                choices = choices + ["少し休む", "一歩引く"][: 3 - len(choices)]
            return {
                "summary": str(parsed["summary"]),
                "choices": [str(c) for c in choices[:3]],
                "next_step": str(parsed["next_step"]),
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

この日の全体の雰囲気・エネルギーに基づいて、今日の占い（要約・選択肢3つ・次の一歩）を JSON で出力してください。"""


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

{sign_ja}（太陽が{sign}にある人）向けの今日の占いを、上記の天体配置を踏まえて JSON で出力してください。"""


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
