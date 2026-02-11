# Figma実装コンテキスト - Daily Zodiac

**目的**: Figma MCP でデザイン実装する際、プロジェクトを正しく理解させるための参照ドキュメント  
**対象**: `get_design_context` 等で取得したデザインを、本プロジェクトの規約に従って実装する際のコンテキスト

**参照元**: `rules/common/rules_figma_mcp.md`（必須フロー・アセットルール）

---

## 0. クイックリファレンス

| 項目 | 本プロジェクト |
|------|----------------|
| テンプレート | Jinja2 |
| マークアップ | HTML5、`class`（`className` ではない） |
| スタイル | Tailwind CSS（CDN、ビルドなし） |
| 背景色 | `bg-zinc-950` |
| カード | `bg-white/10 ring-1 ring-white/15 backdrop-blur-xl` |
| 角丸 | `rounded-2xl`（大）、`rounded-xl`（中） |
| アセット配置 | `assets/images/` |

---

## 1. プロジェクト概要

| 項目 | 内容 |
|------|------|
| **名前** | Daily Zodiac（今日の星座占い） |
| **種類** | 静的占いWebアプリ |
| **配信** | GitHub Pages（静的ファイルのみ） |
| **生成** | Python + Jinja2 で日次生成、出力は `site/` 配下 |

---

## 2. 技術スタック（必須遵守）

| レイヤー | 採用技術 | 注意 |
|----------|----------|------|
| **テンプレート** | Jinja2 | `{% extends %}`, `{% block %}`, `{% include %}` |
| **マークアップ** | HTML5 | セマンティックタグ優先 |
| **スタイル** | Tailwind CSS（CDN） | `class=` でユーティリティクラス。ビルドなし |
| **フレームワーク** | なし | React / Next.js / Vue は使用しない |

**重要**: Figma MCP のデフォルト出力は React + Tailwind。**必ず Jinja2 + HTML + Tailwind に変換**すること。

---

## 3. ディレクトリ構成

```
daily-zodiac/
├── templates/           # Jinja2 テンプレート（編集対象）
│   ├── base.html       # 共通レイアウト（ヘッダー、ヒーロー、広告枠、コンテンツブロック）
│   ├── hero_content.html  # 結果コンテンツ（要約・選択肢・次の一歩・他星座）
│   ├── index.html      # 入口ページ用
│   └── sign.html       # 星座結果ページ用
├── assets/             # 静的アセット
│   └── images/         # 画像配置先（Figma から取得した画像はここへ）
├── site/               # 生成出力先（generate.py が生成。直接編集しない）
├── generate.py         # 日次生成スクリプト
└── docs/               # ドキュメント
```

---

## 4. デザインシステム

### 4.1 カラーパレット

| 用途 | Tailwind クラス | 補足 |
|------|-----------------|------|
| 背景（メイン） | `bg-zinc-950` | ダークベース |
| 背景（アクセント） | `bg-fuchsia-500/10`, `bg-amber-400/8` | ぼかし装飾用 |
| テキスト（主） | `text-zinc-50` | 白に近い |
| テキスト（副） | `text-zinc-200/80`, `text-zinc-200/60` | 透明度で階層 |
| カード/パネル | `bg-white/5`, `bg-white/10`, `bg-white/12` | 半透明 |
| ボーダー/リング | `ring-1 ring-white/10`, `ring-white/12`, `ring-white/15` | 細い枠 |
| CTA ボタン | `bg-white text-zinc-950` | 反転 |
| グラデーション（オーバーレイ） | `bg-gradient-to-t from-zinc-950/90 via-zinc-950/40 to-transparent` | ヒーロー画像上 |

### 4.2 タイポグラフィ

| 用途 | クラス | 例 |
|------|--------|-----|
| ラベル | `text-xs text-zinc-200/80` | セクションラベル |
| 本文 | `text-sm leading-relaxed text-zinc-50` | 要約・説明 |
| 見出し（小） | `text-sm font-semibold` | カード内 |
| 見出し（中） | `text-base font-semibold tracking-tight` | ヘッダー |
| 見出し（大） | `text-xl md:text-2xl font-semibold tracking-tight` | ヒーロー |
| 注釈 | `text-[11px] text-zinc-200/70` | 注意書き・広告ラベル |

### 4.3 スペーシング・レイアウト

| 用途 | クラス |
|------|--------|
| ページ余白 | `mx-auto max-w-5xl px-4 py-6` |
| セクション間 | `mb-4`, `mb-5`, `mb-6` |
| カード内余白 | `p-4`, `p-5`, `p-6`, `sm:p-8` |
| グリッドギャップ | `gap-3`, `gap-5`, `gap-x-2 gap-y-1` |

### 4.4 コンポーネントパターン

**カード（選択肢・次の一歩）**
```html
<div class="rounded-2xl bg-white/10 ring-1 ring-white/15 backdrop-blur-xl p-4 ...">
```

**カード（リンク・ホバー付き）**
```html
<a href="..." class="block rounded-2xl bg-white/10 ring-1 ring-white/15 backdrop-blur-xl p-4 text-left hover:bg-white/12 transition">
```

**パネル（セクション）**
```html
<section class="rounded-2xl ring-1 ring-white/12 bg-white/5 backdrop-blur-xl overflow-hidden">
```

**CTA ボタン**
```html
<a href="..." class="shrink-0 rounded-2xl bg-white text-zinc-950 px-4 py-2 text-sm font-semibold hover:bg-zinc-100 transition">
```

### 4.5 インタラクション・トランジション

- **ホバー**: `hover:bg-white/12`（カード）、`hover:bg-zinc-100`（白ボタン）、`hover:text-white`（テキストリンク）
- **トランジション**: `transition` を付与（duration 指定なし = デフォルト）

---

## 5. テンプレート構造（base.html）

```
<body>
  <!-- 背景（固定） -->
  <div class="fixed inset-0 -z-10">...</div>

  <main class="mx-auto max-w-5xl px-4 py-6">
    <header>ロゴ・タイトル</header>
    <section>キービジュアル（aspect-[2/3]）</section>
    <aside>広告枠（Ad Slot 300×48）</aside>
    <section>{% block content %}{% endblock %}</section>
  </main>
</body>
```

- **Tailwind CDN**: `<script src="https://cdn.tailwindcss.com"></script>` を head に記述
- **lang**: `ja`
- **base href**: `{{ base_path }}` で相対パス解決

---

## 6. アセットの扱い

| ルール | 詳細 |
|--------|------|
| 配置先 | `assets/images/` |
| Figma の localhost ソース | そのまま使用。プレースホルダーを作成しない |
| 新規アイコンパッケージ | 追加禁止。アセットは Figma ペイロードから取得 |
| 参照パス | 出力時は `./画像名` など相対パス（generate.py の `img_src` 参照） |

---

## 7. 既存コンポーネントの再利用

実装前に以下を確認し、可能な限り再利用する：

- `templates/base.html` のレイアウト構造（ヘッダー、ヒーロー、広告枠、コンテンツ）
- `templates/hero_content.html` のカード・グリッド・リンクパターン
- 上記デザインシステムのクラス（BEM ではなく Tailwind ユーティリティ）

---

## 8. 変換チェックリスト（Figma → 本プロジェクト）

実装時、以下を必ず確認：

- [ ] React/JSX ではなく **HTML** で出力
- [ ] `className` ではなく **`class`**
- [ ] Tailwind クラスは上記デザインシステムに合わせて調整
- [ ] Jinja2 変数が必要な箇所は `{{ ... }}` でプレースホルダー
- [ ] 画像は `assets/images/` に配置し、相対パスで参照
- [ ] 広告枠は `aside` + `ad-slot` クラスで固定位置を維持

---

## 9. Figma 実装時の注意（よくある誤り）

| 誤り | 正しい |
|------|--------|
| `className=` | `class=` |
| `<div className="...">` | `<div class="...">` |
| React コンポーネント | Jinja2 `{% block %}`, `{% include %}` |
| 新規 npm パッケージ | 使用禁止。Tailwind CDN のみ |
| プレースホルダー画像 | Figma の localhost ソースをそのまま使用 |

---

**最終更新**: 2026-02-11  
**参照**: `rules/common/rules_figma_mcp.md`, `rules/PROJECT_AGENT.md`
