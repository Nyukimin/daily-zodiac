# daily-zodiac

日次星座占いの静的サイト（GitHub Pages + GitHub Actions）

## デプロイ先

https://nyukimin.github.io/daily-zodiac/

## 更新スケジュール

- **cron**: `0 16 * * *` = UTC 16:00 = JST 01:00（毎日）
- **日付基準**: JST（Asia/Tokyo）

## ローカル確認（PowerShell）

```powershell
$env:BASE_PATH="/"
python .\generate.py
python -m http.server 8000 --bind 127.0.0.1 --directory .\site
```

ブラウザで http://localhost:8000/ を開く。

**ERR_EMPTY_RESPONSE が出る場合**: Windows では `--bind 127.0.0.1` を付けると解消することが多い。
