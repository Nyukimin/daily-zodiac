---
name: TDD 実装計画
overview: 実装仕様_02 に沿って TDD で assets/templates.json、テスト3本、generate.py の関数分割を行い、pytest を Actions に組み込む。
todos: []
isProject: false
---

# 実装仕様_02 に沿った TDD 実装計画

## 現状との差分


| 項目           | 現状             | 仕様_02                                                                            |
| ------------ | -------------- | -------------------------------------------------------------------------------- |
| データソース       | ハードコード（ダミー）    | `assets/templates.json`                                                          |
| テスト          | なし             | `tests/` に3本                                                                     |
| 関数           | `build_one` 直接 | `load_templates`, `select_template`, `build_one_from_templates`, `generate_site` |
| requirements | 空              | `pytest>=8.0.0`                                                                  |
| Actions      | テストなし          | 生成前に `pytest` 実行                                                                 |


---

## 実装順序（TDD）

### Step 1: assets/templates.json を作成

- 12星座 × 各1〜7個のテンプレ（最低1、推奨7以上）
- 各要素: `{ "summary": "...", "choices": ["a","b","c"], "next_step": "..." }`
- `choices` は2〜3個（MVP は3固定可）
- 煽らない・断定しない文言

参照: [docs/実装仕様/実装仕様_02.md](docs/実装仕様/実装仕様_02.md) 3節

---

### Step 2: tests/test_templates.py（先に書く）

- `assets/templates.json` が存在する
- 12星座キーが揃っている（`SIGNS` と一致）
- 各星座の配列長が1以上
- 各テンプレに `summary`, `choices`, `next_step` があり、`choices` は2〜3個

実行: `pytest tests/test_templates.py -v` → 最初は `load_templates` 未実装で失敗する想定

---

### Step 3: load_templates() 実装

- シグネチャ: `load_templates(path: str | Path) -> dict`
- `json.load` で読み込み、そのまま返す
- [generate.py](generate.py) に追加

---

### Step 4: tests/test_determinism.py（先に書く）

- `select_template(templates, sign, date_str)` が同じ入力で同じ結果を返す
- 別日（`date_str` 違い）では、同一星座でも別テンプレになり得る（配列長>1の場合）
- ロジック: `idx = int(date_str.replace("-","")) % len(templates[sign])`

---

### Step 5: select_template() 実装

- シグネチャ: `select_template(templates: dict, sign: str, date_str: str) -> dict`
- `yyyymmdd = int(date_str.replace("-", ""))`
- `idx = yyyymmdd % len(templates[sign])`
- `return templates[sign][idx]`

---

### Step 6: tests/test_generate_outputs.py（先に書く）

- `generate_site(date_str="2026-02-10", out_dir="site")` を実行
- 以下のファイルが生成される:
  - `site/index.html`
  - `site/{sign}/index.html`
  - `site/{sign}/index.json`
- JSON に必須キー（`date`, `sign`, `sign_ja`, `summary`, `choices`, `next_step`）がある
- HTML に `<meta charset="utf-8">` と `<base href="...">` が含まれる
- テスト用に一時ディレクトリを使用（`tmp_path`）

---

### Step 7: generate_site() 実装と main のリファクタ

- シグネチャ: `generate_site(date_str: str | None = None, out_dir: str | Path = "site") -> None`
- `date_str` が None なら `get_jst_date_str()` を使用
- `load_templates("assets/templates.json")` → 各 sign で `select_template` → `build_one_from_templates` 相当の dict を組み立て
- 既存の `write_index`, `write_sign_files`, `render_html` を流用
- 例外時は `fallback_one` で星座単位フォールバック
- `if __name__ == "__main__": generate_site()` に変更

---

### Step 8: requirements.txt と Actions 更新

- [requirements.txt](requirements.txt): `pytest>=8.0.0` を追加
- [.github/workflows/pages.yml](.github/workflows/pages.yml): `Generate site` の前に `Run tests` ステップを追加

```yaml
- name: Run tests
  run: pytest -q
```

---

### Step 9: 動作確認

- ローカル: `pytest -q` が通る
- ローカル: `BASE_PATH="/" python generate.py` で生成
- 本番デプロイ確認（必要に応じて push）

---

## ファイル変更一覧


| ファイル                             | 操作               |
| -------------------------------- | ---------------- |
| `assets/templates.json`          | 新規作成             |
| `tests/test_templates.py`        | 新規作成             |
| `tests/test_determinism.py`      | 新規作成             |
| `tests/test_generate_outputs.py` | 新規作成             |
| `generate.py`                    | 関数追加・main リファクタ  |
| `requirements.txt`               | pytest 追加        |
| `.github/workflows/pages.yml`    | Run tests ステップ追加 |


---

## 維持する既存仕様

- `SIGNS`, `SIGN_JA`, `BASE_PATH` はそのまま
- `render_html`, `write_sign_files`, `write_index`, `fallback_one` は流用
- HTML 構造・JSON スキーマは変更なし

