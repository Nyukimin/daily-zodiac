# Daily Zodiac HTML 構造図

最終更新: 2026-02-11

## 全体構成（テンプレート継承）

```
index.html ─────┐
                ├─→ extends base.html
sign.html ──────┘         │
                         └─→ {% block content %} ← include hero_content.html
```

---

## base.html の DOM 構造（キャラクター図）

```
html
├── head
│   ├── meta charset
│   ├── meta viewport
│   ├── base
│   ├── title
│   └── script (Tailwind CDN)
│
└── body
    │
    ├── [背景層] div.fixed.-z-10
    │   ├── div (zinc-950 塗りつぶし)
    │   ├── div (fuchsia blur 円)
    │   └── div (amber blur 円)
    │
    └── main (flex flex-col min-h-screen)
        │
        ├── nav (星座切り替えタブ)
        │   └── ul
        │       ├── li → a 「全体運」
        │       └── li → a 「牡羊座」…「魚座」(×12)
        │
        ├── section (キービジュアル h-[28vh])
        │   └── div.flex
        │       ├── div (左: テキスト)
        │       │   ├── p {{ data.date }}
        │       │   ├── h2 「今日の○○」
        │       │   └── p {{ data.summary }} (45字で省略)
        │       └── div (右: イラスト)
        │           ├── img (キービジュアル)
        │           └── div (グラデーションオーバーレイ)
        │
        ├── aside (広告枠)
        │   ├── p 「スポンサーリンク」
        │   └── div.ad-slot (300×48)
        │
        └── section (結果コンテンツ flex-1)
            └── {% block content %}
                    └── hero_content.html (include)
```

---

## hero_content.html の DOM 構造（結果エリア詳細）

```
div (flex flex-col flex-1)
│
├── div (アドバイス ボックス flex-1)
│   └── p {{ data.advice }}
│
└── p (注意書き shrink-0)
    └── ※占いは娯楽です。医療・法律・投資…
```

---

## 画面レイアウト（ビジュアル）

```
┌─────────────────────────────────────────┐
│ 全体運 | 牡羊座 | 牡牛座 | … | 魚座      │  ← nav
├─────────────────────────────────────────┤
│ ┌───────┬─────────────────────────┐   │
│ │日付    │                         │   │
│ │今日の○ │     イラスト            │   │  ← キービジュアル
│ │要約…  │   (グラデーション)       │   │
│ └───────┴─────────────────────────┘   │
├─────────────────────────────────────────┤
│ スポンサーリンク                        │
│ ┌─────────────────┐                    │  ← 広告枠
│ │ Ad Slot (300×48)│                    │
│ └─────────────────┘                    │
├─────────────────────────────────────────┤
│                                         │
│  {{ data.advice }}                      │  ← 結果コンテンツ
│                                         │   (アドバイスのみ)
│                                         │
├─────────────────────────────────────────┤
│ ※占いは娯楽です。…                      │  ← 注意書き
└─────────────────────────────────────────┘
```

---

## テンプレート・継承関係

```
base.html
    │
    ├── index.html  (extends, is_home=True)
    │       block content → hero_content.html
    │
    └── sign.html   (extends, is_home=False)
            block content → hero_content.html
```
