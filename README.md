# make it fit

旧称 ma.。このリポジトリはブラウザーで動くHTML版です。

案件の「図面・部材」タブで、解析済みの部材と図面を対応づけて確認・編集・保存できます。部材データを読み込み、部材一覧または図面の番号を選んでください。

機能・入力形式・保存互換: [docs/drawing-parts.md](docs/drawing-parts.md)

検証: Node.js 22以上で `npm test`。ブラウザー検証は `npm run test:browser`（Python Playwright / Chromium）。実案件の図面と部材データはローカルで扱い、公開ソースへ同梱しません。
