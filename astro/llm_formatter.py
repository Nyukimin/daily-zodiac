"""Gemini Lite を用いた占い文章成形。"""

from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, Tuple

# 環境変数 LLM_API_KEY または GEMINI_API_KEY を使用。未設定時は None を返す。
# LLM_EVAL_DISABLED=1 で評価をスキップ（CI 等で使用）

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

    profile = config.get("profile")
    role = config.get("role")
    if profile:
        profile_str = str(profile).replace("\n", " ").strip()
        if role:
            parts.append(f"あなたはRANAIという占い師です。{profile_str}。あなたの役割は{role}ことです。")
        else:
            parts.append(f"あなたはRANAIという占い師です。{profile_str}。")
    elif role:
        parts.append(f"あなたは{role}です。")

    tone = config.get("tone")
    if tone and isinstance(tone, list):
        tone_str = "、".join(str(t) for t in tone)
        parts.append(f"{tone_str}トーンで書いてください。")

    avoid = config.get("avoid")
    if avoid and isinstance(avoid, list):
        avoid_str = "、".join(str(a) for a in avoid)
        parts.append(f"以下を避けてください: {avoid_str}。")

    advice_req = config.get("advice")
    if advice_req and isinstance(advice_req, list):
        advice_str = "、".join(str(a) for a in advice_req)
        parts.append(f"アドバイスでは{advice_str}。")

    output = config.get("output", {})
    if isinstance(output, dict):
        schema = output.get("schema")
        strict = output.get("strict", True)
        if schema and isinstance(schema, dict):
            json_example = json.dumps(schema, ensure_ascii=False)
            length_note = " summary は約200文字程度、advice は約200文字程度でそれぞれ出力してください。"
            if strict:
                parts.append(f"必ず次の JSON 形式のみで応答してください（他に説明は不要）。{length_note} 形式: {json_example}")
            else:
                parts.append(f"次の JSON 形式で応答してください。{length_note} 形式: {json_example}")

    if not parts:
        return _DEFAULT_SYSTEM_INSTRUCTION
    return "".join(parts)


_MAX_EVAL_ATTEMPTS = 3

_EVAL_SYSTEM = """あなたは占い文章の品質評価者です。
与えられた占い結果・アドバイスについて、次の2点を評価してください。
1. 日本語の口語として自然で、文法的に破綻していないか
2. RANAI のキャラクター設定（穏やか、寄り添う、断定しない、煽らない等）に合っているか
3. 避けるべき表現（煽り、断定、緊急性の演出等）を含んでいないか
4. アドバイスは簡単にでき、具体的か

必ず次の JSON 形式のみで応答してください:
{"pass": true または false, "score": 1以上5以下の整数, "reason_summary": "要約の簡潔な評価", "reason_advice": "アドバイスの簡潔な評価"}"""


def _call_evaluator(
    client: Any,
    summary: str,
    advice: str,
    config: Dict[str, Any],
) -> Tuple[bool, float]:
    """LLM で占い結果を評価。(pass, score) を返す。失敗時は (False, 0.0)。"""
    try:
        from google.genai import types
    except ImportError:
        return (False, 0.0)

    profile = str(config.get("profile", "")).replace("\n", " ").strip()
    tone = config.get("tone", [])
    tone_str = "、".join(str(t) for t in tone) if isinstance(tone, list) else str(tone)
    avoid = config.get("avoid", [])
    avoid_str = "、".join(str(a) for a in avoid) if isinstance(avoid, list) else str(avoid)
    advice_req = config.get("advice", [])
    advice_str = "、".join(str(a) for a in advice_req) if isinstance(advice_req, list) else str(advice_req)

    prompt = f"""【RANAI のキャラクター設定】
- プロファイル: {profile}
- トーン: {tone_str}
- 避けること: {avoid_str}
- アドバイスの条件: {advice_str}

【評価対象】
占い結果: {summary}
アドバイス: {advice}

上記の評価基準に基づき、JSON のみで応答してください。"""

    try:
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=_EVAL_SYSTEM,
                temperature=0,
            ),
        )
        text = getattr(response, "text", None) or str(response)
        if not text:
            return (False, 0.0)
        parsed = _parse_json_response(text)
        if not parsed:
            return (False, 0.0)
        passed = bool(parsed.get("pass", False))
        score = int(parsed.get("score", 0))
        score = max(1, min(5, score))
        return (passed, float(score))
    except Exception:
        return (False, 0.0)


def _evaluate_result(
    result: Dict[str, Any],
    client: Any,
    config: Dict[str, Any],
) -> Tuple[bool, float]:
    """占い結果を LLM で評価。(pass, score) を返す。"""
    if not result or "summary" not in result or "advice" not in result:
        return (False, 0.0)
    if os.environ.get("LLM_EVAL_DISABLED") == "1":
        return (True, 5.0)
    return _call_evaluator(
        client,
        str(result["summary"]),
        str(result["advice"]),
        config,
    )


def _call_llm_once(
    client: Any,
    prompt: str,
    system_instruction: str,
) -> Dict[str, Any] | None:
    """LLM を1回呼び出し、{summary, advice} の dict を返す。失敗時は None。"""
    try:
        from google.genai import types

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
        parsed = _parse_json_response(text)
        if parsed and "summary" in parsed and "advice" in parsed:
            return {
                "summary": str(parsed["summary"]),
                "advice": str(parsed["advice"]),
            }
    except Exception:
        pass
    return None


def format_with_llm(
    astro_data: Dict[str, Any],
    scope: str,
    sign_ja: str | None = None,
) -> Dict[str, Any] | None:
    """占星術データを Gemini で文章成形し、{summary, advice} を返す。

    占い結果・アドバイスを LLM で評価する（日本語口語として成立、RANAI キャラに合致）。
    最大3回までリトライ。1回で合格ならその結果を返す。
    3回とも不合格の場合は、スコアが最も高い結果を返す。
    LLM_EVAL_DISABLED=1 で評価をスキップ（その場合1回目の結果をそのまま返す）。

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
    except ImportError:
        return None

    if scope == "global":
        prompt = _build_global_prompt(astro_data)
    else:
        prompt = _build_sign_prompt(astro_data, scope, sign_ja or scope)

    system_instruction = _build_system_instruction()
    client = genai.Client(api_key=api_key)
    config = _load_personality_config() or {}

    best: Dict[str, Any] | None = None
    best_score = -1.0

    for attempt in range(_MAX_EVAL_ATTEMPTS):
        if attempt > 0:
            time.sleep(1)  # レート制限対策
        result = _call_llm_once(client, prompt, system_instruction)
        if result is None:
            continue

        time.sleep(1)  # 評価呼び出し前のレート制限対策
        passed, score = _evaluate_result(result, client, config)
        if passed:
            return result

        if score > best_score:
            best_score = score
            best = result

    return best


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
