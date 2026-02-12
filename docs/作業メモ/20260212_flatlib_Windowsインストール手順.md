# flatlib Windows インストール手順

## 概要

flatlib は pyswisseph（Swiss Ephemeris）に依存します。pyswisseph は Windows でビルドが難しいため、**Python 3.11** 環境で事前ビルド wheel を使います。

## 方法1: Conda（推奨）

```powershell
cd c:\GenerativeAI\daily-zodiac
conda env create -f environment.yml
conda activate daily-zodiac
pip install flatlib --no-deps
```

## 方法2: 既存の Python 3.11 環境で手動インストール

```powershell
# 1. pyswisseph を先にインストール（wheel 使用）
pip install pyswisseph==2.10.3.2

# 2. flatlib を --no-deps でインストール（古い pyswisseph を上書きしないため）
pip install flatlib --no-deps

# 3. その他
pip install -r requirements.txt
```

## 動作確認

```powershell
conda activate daily-zodiac
cd c:\GenerativeAI\daily-zodiac
python -c "from astro.engine import get_chart_data; print(get_chart_data('2026-02-12'))"
```

## 注意

- **Python 3.12/3.13**: pyswisseph に wheel がなく、ソースビルドが必要（Microsoft C++ Build Tools 必須）
- **requirements.txt**: `pip install -r requirements.txt` 単体では flatlib が古い pyswisseph を要求し競合する場合あり。上記いずれかの方法でインストールすること。
