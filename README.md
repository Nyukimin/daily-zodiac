# daily-zodiac

日次星座占いの静的サイト（GitHub Pages + GitHub Actions）

## デプロイ先

https://nyukimin.github.io/daily-zodiac/

## 更新スケジュール

- **cron**: `0 16 * * *` = UTC 16:00 = JST 01:00（毎日）
- **日付基準**: JST（Asia/Tokyo）

---

## セットアップ

### 必要環境

- Python 3.11（flatlib / pyswisseph の Windows wheel 対応版のため）
- `.env` に `LLM_API_KEY` を設定（Gemini API キー）

### 方法1: Conda（Windows 推奨）

```powershell
conda env create -f environment.yml
conda activate daily-zodiac
pip install flatlib --no-deps
```

### 方法2: pip（Linux / macOS）

```bash
pip install -r requirements.txt
```

### 環境変数

プロジェクトルートに `.env` を作成:

```
LLM_API_KEY=your_gemini_api_key
```

---

## ローカル確認

```powershell
conda activate daily-zodiac   # または通常の Python 環境
$env:BASE_PATH="/"
python .\generate.py
python -m http.server 8000 --bind 127.0.0.1 --directory .\site
```

ブラウザで http://localhost:8000/ を開く。

**ERR_EMPTY_RESPONSE が出る場合**: Windows では `--bind 127.0.0.1` を付けると解消することが多い。

---

## 補足

- **flatlib（Windows）**: pyswisseph のビルド済み wheel は Python 3.11 まで。3.12/3.13 の場合はビルドツールが必要。詳細は `docs/作業メモ/20260212_flatlib_Windowsインストール手順.md`
