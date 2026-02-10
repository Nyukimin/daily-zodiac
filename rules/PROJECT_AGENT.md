# PROJECT_AGENT.md - Daily Zodiac プロジェクトルール

**プロジェクト名**: Daily Zodiac（占いWebアプリ）

---

## 0. グローバル宣言

### 0.1 マネージャ層の実装禁止

あなたはマネージャで、agentオーケストレーターです。
あなたは絶対に実装せず、全てsubagentやtask agent に委託すること。
タスクは超細分化し、PDCAサイクルを構築すること。

**補足**: 本プロジェクトは小規模（generate.py + workflow 中心）のため、単一タスクの場合は task agent が実装を兼任する運用も可。委託先が不明な場合は実装前に方針を確認すること。

## 1. コア原則

### 1.1 「消えずに回る」占い体験
- **目的**: 既存の星座占い資産を核に、Webで配布できる占い体験を、最小の運用コストで外部公開する。
- **収益化**: 広告（PV/クリック）を想定。計測は最小限とし、個人追跡はしない。
- **運用**: サーバ管理をしない。常時稼働のAPI/DBは持たない。

### 1.2 前提（厳守）
- **占いの位置づけ**: 娯楽として扱う。不安・恐怖・罪悪感で誘導しない（煽り語／断定／緊急性の演出を避ける）。
- **外部依存**: 壊れる前提で設計する。APIが落ちても「結果は必ず返す」（フォールバックで体験継続）。
- **表示**: 固定フォーマットで統一し、データ差を吸収する。
- **再現性**: 同日・同星座は固定（結果が何度も変わらない）。乱数で毎回変える占いは行わない。

### 1.3 静的配信・日次更新
- **ホスティング**: GitHub Pages（静的配信）。アクセス集中でも壊れにくい。
- **更新**: GitHub Actions で Python を毎日1回だけ実行し、HTML/JSON を生成して Pages へデプロイする。
- **生成物**: その日のスナップショットとして扱い、当日中に内容が揺れない。

---

## 2. プロジェクト構造

- **ルート直下**
  - `generate.py`: 日次生成スクリプト（JST日付取得、12星座分のHTML/JSON出力）
  - `requirements.txt`: Python依存（必要なら。空でも可）
- `site/`: 生成物の出力先（Actionsが生成。コミット不要でも可）
  - `index.html`: 入口ページ（12星座へのリンク一覧）
  - `{sign}/`: 各星座（例: `aries/`, `taurus/`）
    - `index.html`, `index.json`: 固定フォーマット（要約・選択肢・次の一歩）
- `.github/workflows/`: CI/CD
  - `pages.yml`: ビルド（generate.py実行）→ upload-pages-artifact → deploy-pages
- `docs/`: ドキュメント（仕様書、実装仕様など）
  - `docs/作業メモ/`: 作業メモはここに格納する。ファイル名は他文書と同様 **JST プレフィックス**（`YYYYMMDD_HHMMSS_説明的なタイトル.md`）を付ける。
- `rules/`: プロジェクト・共通ルール（PROJECT_AGENT.md, common/）。**`rules_domain.md` は削除済み。プロジェクトの進捗に応じて必要になった時点で生成し、.cursorrules に参照を追加する。**

**ローカル確認**: 手元で `python generate.py` を実行すると `site/` が生成される。`site/index.html` および `site/{sign}/index.html`・`index.json` の有無・内容でMVPを検証できる。

---
## 3. ドキュメントルール

### 3.1 命名規則（必須）

**重要**: `docs/`フォルダ配下のすべてのファイル名は**必ず日本語**を使用すること。

- **適用範囲**: `docs/`直下およびすべてのサブフォルダ内のファイル（`docs/作業メモ/` を含む）
- **形式**: `YYYYMMDD_HHMMSS_説明的なタイトル.md`
- **JST**: 日付・時刻のプレフィックスは **必ず JST**（日本標準時）で付ける。**作業メモに限らず、docs/ 配下の他文書も同じく JST を必ず使う。**
- **タイトル部分**: 日本語で記述すること（英語は使用不可）
- **例（正）**: 
  - `20260210_120000_仕様書.md`
  - `20260210_120000_実装仕様.md`
  - `20260210_120000_星座フォーマット設計.md`
  - `仕様書.md`（直下の既存ファイルも日本語）
- **例（誤）**: 
  - `20260210_120000_spec.md` ❌
  - `specification.md` ❌

### 3.2 各ファイル・フォルダの用途

- **`docs/` 直下**: 本プロジェクトでは仕様・実装仕様を直下に配置。
  - **一次仕様**: `docs/仕様書.md`（目的・方式・UX・フォーマット・運用）
  - **実装仕様**: `docs/実装仕様.md`（Done定義・構成・generate.py/pages.yml の詳細・コピペ用コード）
- **`docs/作業メモ/`**: 作業メモはすべてここに格納する。ファイル名は上記と同様 **JST プレフィックス**を必ず付ける（`YYYYMMDD_HHMMSS_説明的なタイトル.md`）。例: `20260210_181206_serena起動手順.md`, `20260210_181207_PROJECT_AGENTレビューと修正.md`（プレフィックスは作成時の JST を使用）。**リネーム時は必ず `mv`（Rename-Item / Move-Item）で行い、ファイルを作り直さない。**
- **サブフォルダを使う場合**（任意）:
  - `docs/仕様/`: 要件定義書・機能仕様書など。命名: `YYYYMMDD_HHMMSS_説明的なタイトル.md` (JST、日本語必須)
  - `docs/実装仕様/`: 技術的実装詳細。命名: 同上。
  - `docs/調査/`: 不具合分析・技術調査。詳細は `rules/common/rules_logging.md` を参照。命名: `YYYYMMDD_hhmmss_説明的なタイトル.md`
---
## 4. 技術スタック詳細

### 4.1 Python（生成スクリプト）
- **実行**: 常時稼働しない。GitHub Actions 内でのみ実行（日次1回）。
- **役割**: JSTで `YYYY-MM-DD` を決定し、12星座を走査して `site/` 配下に HTML/JSON を出力する。
- **日付**: `datetime.now(timezone(timedelta(hours=9)))` で JST を取得し `strftime("%Y-%m-%d")`。
- **推奨関数**: `get_jst_date_str()`, `build_one(sign, date_str)`, `fallback_one(sign, date_str, err)`, `render_html(data)`, `write_files()`。星座ループ内で try/except し、例外時は `fallback_one()` で継続。

### 4.2 GitHub Actions
- **トリガー**: `push`（main）, `schedule`（毎日1回・UTC cron）, `workflow_dispatch`（手動）。
- **権限**: `contents: read`, `pages: write`, `id-token: write`。
- **ジョブ**: checkout → setup-python → pip install（requirements.txt）→ `python generate.py` → upload-pages-artifact → deploy-pages。
- **Python**: 3.12 を推奨（実装仕様に準拠）。

### 4.3 GitHub Pages・出力フォーマット
- **配信**: 静的ファイルのみ。`site/` を artifact としてアップロードし、deploy-pages で反映。
- **JSON必須キー**: `date`, `sign`, `summary`, `choices`, `next_step`。同日・同星座で固定。
- **HTML**: H1（星座/日付）、summary（`<p>`）、choices（`<ol>`/`<ul>`）、next_step（`<p>`）。広告枠はプレースホルダで固定位置を確保。
- **星座スラッグ**: aries, taurus, gemini, cancer, leo, virgo, libra, scorpio, sagittarius, capricorn, aquarius, pisces（順序固定）。
- **フォールバック**: 星座単位で例外時は `summary` を「{sign} の今日の要約（フォールバック）」、`choices`/`next_step` を固定文言で出力し、生成全体を止めない。

---

## 5. Git運用ルール

### 5.1 コミットメッセージ（UTF-8日本語対応）

**重要**: コミットメッセージは**必ず日本語**で記述すること。

- **文字エンコーディング**: UTF-8
- **問題**: PowerShellから `git commit -m` で日本語を含むメッセージを直接指定すると、エンコーディングエラーが発生する場合がある
- **解決方法**: コミットメッセージをファイルから読み込む方法を使用する

#### 推奨方法

1. **コミットメッセージファイルを作成**:
   ```bash
   # commit_message.txt を作成（UTF-8で保存）
   ```

2. **ファイルからコミット**:
   ```bash
   git commit -F commit_message.txt
   ```

3. **一時ファイルを削除**:
   ```bash
   # コミット後、commit_message.txt を削除
   ```

#### コミットメッセージの形式

- **形式**: `種類: 簡潔な説明（詳細な説明）`
- **種類**: `docs`, `feat`, `fix`, `refactor`, `style`, `test` など
- **例**: 
  - `docs: 仕様書にフォールバック方針を追記`
  - `feat: generate.py と pages.yml を追加（MVP）`
  - `fix: JST日付取得を timezone(timedelta(hours=9)) に統一`

---

## 6. 参照ルール

- **一次仕様（本プロジェクト）**: `docs/仕様書.md`, `docs/実装仕様.md` を最優先で参照すること。
- **ドメインルール**: `rules/rules_domain.md` は現状なし。プロジェクトの進捗（占いロジック・フォーマット・運用などドメイン固有のルールが増えたタイミング）に応じて生成し、`.cursorrules` に `@rules/rules_domain.md` を追加する。
- **共通ルール**: `rules/common/GLOBAL_AGENT.md`
