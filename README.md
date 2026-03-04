# sw-redirect-micro-service

## このリポジトリ
work_idを介してmicroCMSに保存されているredirect_urlに転送するマイクロサービス

## ディレクトリ構成
```
.
├── encrypt.py                      # ローカル用encryptスクリプト
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

## ローカル動作確認
- dockerコンテナを立ち上げて、APIを叩いて実行
```bash
docker build -t sw-redirect-lambda .
docker run -p 9000:8080 sw-redirect-lambda
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{
    "httpMethod": "GET",
    "path": "/redirect",
    "queryStringParameters": {
      "id": "xxx"
    }
  }'
```

## work_idのencrypt
- ローカルの場合
   `python encrypt.py <work_id>`

## サンプルURL
`https://dqqvl5huzxx3uy7vih5xn5elly0poazt.lambda-url.ap-northeast-1.on.aws/redirect?id=gAAAAABpqAjrwo3tuFfJadLPkOWqw1vOh7rIIE4SbQVy39f5zhuuX6TgwC-8UaNSiuigbjHT0c02ml0LC4u7jR-wpCACSn7AVQ%3D%3D`
※URLエンコード必須

## インフラアーキテクチャ
Client
↓
Cloudflare (CDN + WAF + DDoS)
↓
Lambda Function URL
↓
Lambda