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

## サンプルURL
`https://25hhmbph7d.execute-api.ap-northeast-1.amazonaws.com/redirect/?id=gAAAAABppnemM5vJ0GryVayGiv1DHFT5lRIiL_IV8Ou1DxFJL9bucUYyOuXCEXIKIL7JkWncdRZycALjJ1pZXAONtcAveYW2Jw==`

`https://dqqvl5huzxx3uy7vih5xn5elly0poazt.lambda-url.ap-northeast-1.on.aws/redirect/?id=gAAAAABppnemM5vJ0GryVayGiv1DHFT5lRIiL_IV8Ou1DxFJL9bucUYyOuXCEXIKIL7JkWncdRZycALjJ1pZXAONtcAveYW2Jw==`

`https://dqqvl5huzxx3uy7vih5xn5elly0poazt.lambda-url.ap-northeast-1.on.aws/redirect/?id=gAAAAABpp_sAbVKIVzo8TjlPXiol-4yonoJuiCYK4cOed53CcmBdLzbh2ocvSqIckUP7Fg3rdbERuWgT7gxE5xapBXBqnP-VTQ==`

URLエンコード
`https://dqqvl5huzxx3uy7vih5xn5elly0poazt.lambda-url.ap-northeast-1.on.aws/redirect?id=gAAAAABpqAjrwo3tuFfJadLPkOWqw1vOh7rIIE4SbQVy39f5zhuuX6TgwC-8UaNSiuigbjHT0c02ml0LC4u7jR-wpCACSn7AVQ%3D%3D`


## work_idのencrypt
- ローカルの場合
   `python encrypt.py <work_id>`


## インフラアーキテクチャ
Client
↓
Cloudflare (CDN + WAF + DDoS)
↓
Lambda Function URL
↓
Lambda