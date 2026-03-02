# sw-redirect-micro-service

## このリポジトリ
work_idを介してmicroCMSに保存されているredirect_urlに転送するマイクロサービス

## ディレクトリ構成
```
.
├── main.py                         #ローカル実行用ファイル
├── src/
│   └── handler.py                  # Lambda ハンドラー
├── .github/
│   └── workflows/
│       └── deploy.yml              # Lambda コード更新ワークフロー（OIDC）
└── .gitignore
```

### デプロイ先
mainブランチでpushするとAWS Lambdaにデプロイされる
```bash
git push origin main
```

### ローカル動作確認
- スクリプトとして実行
`uv run python main.py`

- dockerコンテナを立ち上げて、APIを叩いて実行
```bash
docker build -t sw-redirect-lambda .
docker run -p 9000:8080 sw-redirect-lambda
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{
    "httpMethod": "GET",
    "path": "/redirect",
    "queryStringParameters": {
      "url": "https://example.com"
    }
  }'
```