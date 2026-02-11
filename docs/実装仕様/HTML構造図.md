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
    └── main (flex flex-col min-h-screen gap-y-3)
        │
        ├── nav (星座切り替え・横スクロール、min-h-[44px] タップ領域)
        │   └── ul.flex.flex-nowrap
        │       ├── li → a 「全体運」（rounded-lg bg-white/5）
        │       └── li → a 「牡羊座」…「魚座」(×12)
        │
        ├── section (占い結果 min-h-[160px]、ラベルなし)
        │   └── div.flex (pt-3 pb-3)
        │       ├── div (左: テキスト flex-[0.9])
        │       │   ├── p {{ data.date }}
        │       │   ├── h2 「今日の○○」
        │       │   └── p {{ data.summary }} (全文表示)
        │       └── div (右: イラスト flex-[1.3] h-[200px])
        │           ├── img (w-[130%] object-contain object-center、高さ指定なし)
        │           └── div (グラデーションオーバーレイ)
        │
        ├── aside (広告枠)
        │   ├── p 「スポンサーリンク」
        │   └── div.ad-slot (300×48)
        │
        └── section (アドバイス・高さ可変)
            └── {% block content %}
                    └── hero_content.html (include)
```

---

## hero_content.html の DOM 構造（結果エリア詳細）

```
div (flex flex-col)
│
├── p (アドバイス ラベル shrink-0)
│
├── div (アドバイス本文・高さ可変)
│   └── p {{ data.advice }}
│
└── p (注意書き shrink-0)
    └── ※占いは娯楽です。医療・法律・投資…
```

---

## 画面レイアウト（ビジュアル）

```
┌─────────────────────────────────────────┐
│ [全体運][牡羊座][牡牛座]… ←横スクロール  │  ← nav (44pxタップ)
├─────────────────────────────────────────┤
│ ┌───────┬─────────────────────────┐   │  ← 占い結果（ラベルなし、pt-3余白）
│ │余白    │                         │   │
│ │日付    │  イラスト(h200px固定)   │   │  ← キービジュアル
│ │今日の○ │  縦中央・w130%          │   │
│ │要約    │  (全文表示)             │   │
│ │(全文)  │                         │   │
│ │余白    │                         │   │
│ └───────┴─────────────────────────┘   │
├─────────────────────────────────────────┤
│ スポンサーリンク [Ad Slot 300×48]      │
├─────────────────────────────────────────┤
│ アドバイス                              │
│ {{ data.advice }} (全文・折り返し)      │  ← 高さ可変
├─────────────────────────────────────────┤
│ ※占いは娯楽です。…                      │
└─────────────────────────────────────────┘
      ↑ 縦スクロールで全コンテンツ閲覧可能
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
