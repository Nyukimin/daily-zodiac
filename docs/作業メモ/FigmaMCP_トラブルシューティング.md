# Figma MCP トラブルシューティング

**作成日**: 2026-02-11  
**対象**: figma-desktop（Error）・figma（Needs authentication）の解消

**関連**: `docs/作業メモ/20260211_120000_FigmaMCP構築手順.md` セットアップ | `docs/実装仕様/Figma実装コンテキスト.md` 実装時参照

---

## 状況の整理

| サーバー | 表示 | 主な原因 |
|---------|------|----------|
| **figma-desktop** | Error - Show Output、`ECONNREFUSED 127.0.0.1:3845` | Figma デスクトップアプリで MCP が有効化されていない、またはアプリが起動していない |
| **figma** | Needs authentication | Figma アカウントへの認証が未完了 |

---

## 1. figma-desktop（Error）の解消

figma-desktop は **Figma デスクトップアプリが起動しているときのみ** `http://127.0.0.1:3845/mcp` で動作します。  
エラーになる場合は、次を順に確認してください。

### 1.1 必須条件の確認

- [ ] [Figma デスクトップアプリ](https://www.figma.com/downloads/) をインストール済み
- [ ] 最新版にアップデート済み
- [ ] Figma デスクトップアプリを**起動している**
- [ ] デザインファイル（*.fig）を**開いている**

### 1.2 Dev Mode で MCP を有効化

1. Figma デスクトップでデザインファイルを開く
2. ツールバー下部で **Dev Mode** に切り替え（<kbd>Shift</kbd>+<kbd>D</kbd>）
3. インスペクトパネル右側の **「MCP server」** セクションを探す
4. **「Enable desktop MCP server」** をクリック
5. 確認メッセージが出れば有効化完了

### 1.3 よくある見落とし

- **ファイルを開いていない**: MCP サーバーはファイルがアクティブなときのみ起動
- **Web版ではなくデスクトップ版**: ブラウザの Figma では MCP は動作しない
- **ファイアウォール**: `127.0.0.1:3845` がブロックされていないか確認

### 1.4 再接続手順

1. Figma デスクトップアプリを完全終了
2. Figma デスクトップアプリを再起動
3. デザインファイルを開き、Dev Mode → MCP を有効化
4. Cursor を再起動（または MCP サーバーを再接続）

### 1.5 Error - Show Output の確認

Cursor Settings の figma-desktop 行にある **「Show Output」** をクリックし、  
表示されるエラーメッセージの内容を確認してください。

**よくあるエラー**:
- `connect ECONNREFUSED 127.0.0.1:3845` → ポート 3845 で何も待ち受けていない = Figma デスクトップで MCP がオフ

---

## 2. figma（Needs authentication）の解消

figma リモートサーバー（https://mcp.figma.com/mcp）を使うには、Figma アカウント認証が必要です。

### 2.1 認証手順

1. Cursor → Settings → Cursor Settings → **Tools & MCP** を開く
2. **Installed MCP Servers** 内の **figma** を探す
3. 「Needs authentication」の横にある **「Connect」** ボタンをクリック
4. ブラウザが開き、Figma の認証画面が表示される
5. アカウントでログインし、アクセスを許可する

### 2.2 認証後の確認

- 「Connect」が「Connected」などの状態に変わる
- ツール数（例: 5 tools enabled）が表示される

---

## 3. どちらを使うか

| 用途 | 推奨サーバー |
|------|-------------|
| Figma URL からデザインを実装 | **figma**（リモート）※認証が必要 |
| デスクトップで選択中のノードを実装 | **figma-desktop** ※デスクトップアプリ + MCP 有効化が必要 |

両方使える状態にしておくと、用途に応じて切り替えられます。

---

## 4. 接続後の次のステップ

接続が成功したら、**`docs/実装仕様/Figma実装コンテキスト.md`** を参照してデザイン実装を行う。  
本プロジェクトは Jinja2 + HTML + Tailwind 採用（React 非採用）のため、Figma MCP の出力をプロジェクト規約に変換して実装すること。

---

## 5. 参考リンク

- [Figma MCP Server - Tools aren't loading](https://developers.figma.com/docs/figma-mcp-server/tools-not-loading/)
- [Figma MCP Server - Local Desktop Server Setup](https://developers.figma.com/docs/figma-mcp-server/local-server-installation/)
- 本プロジェクト: `docs/作業メモ/20260211_120000_FigmaMCP構築手順.md`
