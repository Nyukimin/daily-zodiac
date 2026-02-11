# ホロスコープ占星術 + Gemini Lite 実装計画（最終版）

## 概要

flatlib のみで占星術データを取得し、Gemini Lite で文章成形した「全体」+「12星座」分の占い結果を生成する。既存の `try_build_from_engine` を実装し、セキュリティ仕様に準拠したフォールバックを維持する。

---

## 1. 全体構成

- **入力**: date_key (YYYY-MM-DD)
- **占星術エンジン**: flatlib（単体）
- **文章成形**: Gemini Lite（gemini-flash-lite-latest）
- **出力**: global 1件 + signs 12件 → `{summary, choices, next_step}`

---

## 2. 技術選定（確定）

| 項目 | 選定 |
|------|------|
| 占星術層 | flatlib のみ（MIT、Swiss Ephemeris 内蔵） |
| LLM モデル | gemini-flash-lite-latest |
| SDK | google-genai |
| ローカル API キー | .env + python-dotenv |

---

## 3. API キー配置

| 環境 | 配置 |
|------|------|
| 本番 | GitHub Repository Secrets → LLM_API_KEY |
| ローカル | プロジェクト直下 .env → LLM_API_KEY=... |

参照: [docs/作業メモ/20260211_172335_APIキー設定手順.md](../作業メモ/20260211_172335_APIキー設定手順.md)

---

## 4. 変更対象ファイル

### 新規
- `astro/__init__.py`
- `astro/engine.py`（get_chart_data）
- `astro/llm_formatter.py`（format_with_llm）

### 既存変更
- `generate.py`: load_dotenv(), try_build_from_engine 実装
- `requirements.txt`: flatlib, google-genai, python-dotenv
- `.github/workflows/pages.yml`: env LLM_API_KEY

---

## 5. 実装ステップ

1. requirements.txt に flatlib, google-genai, python-dotenv を追加
2. astro/engine.py 実装
3. astro/llm_formatter.py 実装（gemini-flash-lite-latest）
4. generate.py 修正（load_dotenv + try_build_from_engine）
5. pages.yml に LLM_API_KEY 注入を追加
6. テスト確認

---

## 6. 参照

- [docs/仕様書/セキュリティーキー仕様.md](../仕様書/セキュリティーキー仕様.md)
