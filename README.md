# make it fit

旧称 ma.。このリポジトリはブラウザーで動くHTML版です。

案件の「図面・部材」タブで解析済みデータを読み込み、「元アプリの設計で開く」を押すと、既存のユニット・構成ツリー・部材編集に取り込みます。寸法・方向・位置が揃う部材は正面・3Dに表示し、材料構成と木目を設定した部材は既存の木取りへ渡せます。部材編集の「元図面を開く」でG番号と読取根拠を確認できます。

図面との照合・入力形式: [docs/drawing-parts.md](docs/drawing-parts.md)。設計への取込・未確定値・材料・木取り・保存互換: [docs/native-drawing-import.md](docs/native-drawing-import.md)。

検証: Node.js 22以上で `npm test`。ブラウザー検証は `npm run test:browser`（Python Playwright / Chromium）。実案件の図面と部材データはローカルで扱い、公開ソースへ同梱しません。

図面を含むローカル版は `python tools/build-drawing-review.py data.drawing-parts.json result.html` で生成します。ホームの「今回の家具を元アプリで開く」で既存の設計画面を開きます。
