"""astro.llm_formatter の LLM 評価・リトライロジックのテスト。"""

import os
from unittest.mock import MagicMock, patch

import pytest

from astro.llm_formatter import (
    _call_evaluator,
    _evaluate_result,
)


def test_evaluate_result_invalid_empty():
    """必須キーが無ければ不合格（client 不要）。"""
    mock_client = MagicMock()
    ok, score = _evaluate_result({}, mock_client, {})
    assert ok is False
    assert score == 0.0


def test_evaluate_result_invalid_partial():
    """advice が無ければ不合格。"""
    mock_client = MagicMock()
    ok, score = _evaluate_result({"summary": "要約のみ"}, mock_client, {})
    assert ok is False
    assert score == 0.0


def test_evaluate_result_disabled_env():
    """LLM_EVAL_DISABLED=1 のときは評価スキップで合格。"""
    mock_client = MagicMock()
    result = {
        "summary": "蓄積してきたものが形になりそうな日。",
        "advice": "ここ1週間でやったことを3つ書き出してみましょう。",
    }
    with patch.dict(os.environ, {"LLM_EVAL_DISABLED": "1"}):
        ok, score = _evaluate_result(result, mock_client, {})
    assert ok is True
    assert score == 5.0
    mock_client.models.generate_content.assert_not_called()


def test_call_evaluator_pass():
    """評価 LLM が pass: true を返すと合格。"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"pass": true, "score": 5, "reason_summary": "OK", "reason_advice": "OK"}'
    mock_client.models.generate_content.return_value = mock_response

    ok, score = _call_evaluator(
        mock_client,
        "蓄積してきたものが形になりそうな日。",
        "ここ1週間でやったことを3つ書き出してみましょう。",
        {"profile": "test", "tone": [], "avoid": [], "advice": []},
    )
    assert ok is True
    assert score == 5.0


def test_call_evaluator_fail():
    """評価 LLM が pass: false を返すと不合格。"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = '{"pass": false, "score": 2, "reason_summary": "不自然", "reason_advice": "抽象的"}'
    mock_client.models.generate_content.return_value = mock_response

    ok, score = _call_evaluator(
        mock_client,
        "不自然な文章abc",
        "抽象的すぎるアドバイス",
        {"profile": "test", "tone": [], "avoid": [], "advice": []},
    )
    assert ok is False
    assert score == 2.0


def test_call_evaluator_invalid_json():
    """評価 LLM の応答が不正 JSON のときは (False, 0.0)。"""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "Invalid response"
    mock_client.models.generate_content.return_value = mock_response

    ok, score = _call_evaluator(
        mock_client,
        "要約",
        "アドバイス",
        {},
    )
    assert ok is False
    assert score == 0.0


def test_format_with_llm_eval_disabled():
    """LLM_EVAL_DISABLED=1 のとき、1回目の結果をそのまま返す（API モック）。"""
    with patch.dict(os.environ, {"LLM_EVAL_DISABLED": "1", "LLM_API_KEY": "test-key"}):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.text = '{"summary": "今日の要約", "advice": "今日のアドバイス"}'
        mock_client.models.generate_content.return_value = mock_response

        with patch("google.genai.Client", return_value=mock_client):
            from astro.llm_formatter import format_with_llm

            result = format_with_llm(
                {"date": "2026-02-10", "sun_sign": "aries", "moon_sign": "taurus", "planets": {}, "moon_phase": ""},
                "global",
            )
    assert result is not None
    assert result["summary"] == "今日の要約"
    assert result["advice"] == "今日のアドバイス"
    # 評価はスキップされるので generate_content は1回のみ（生成のみ）
    assert mock_client.models.generate_content.call_count == 1
