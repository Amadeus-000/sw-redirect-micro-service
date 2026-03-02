# sw-redirect-micro-service

Hello World を返す AWS Lambda マイクロサービス。  

## ディレクトリ構成

```
.
├── src/
│   └── handler.py                  # Lambda ハンドラー
├── .github/
│   └── workflows/
│       └── deploy.yml              # Lambda コード更新ワークフロー（OIDC）
└── .gitignore
```



### 3. main ブランチへ push

```bash
git push origin main
```

```

## ローカル動作確認

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