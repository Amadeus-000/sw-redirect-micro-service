# sw-redirect-micro-service

Hello World を返す AWS Lambda マイクロサービス。  
Python 3.12 ランタイム・AWS CLI で初期セットアップ・GitHub Actions (OIDC) でデプロイします。

## ディレクトリ構成

```
.
├── src/
│   └── handler.py                  # Lambda ハンドラー
├── scripts/
│   └── bootstrap.sh                # 初回セットアップ（OIDC / IAM / Lambda 作成）
├── .github/
│   └── workflows/
│       └── deploy.yml              # Lambda コード更新ワークフロー（OIDC）
└── .gitignore
```

## 前提条件

| 項目 | 備考 |
|------|------|
| Python | 3.12 |
| AWS CLI | v2（初回セットアップ時に管理者権限） |
| openssl | OIDC thumbprint 取得に使用 |

## セットアップ手順

### 1. bootstrap.sh で初期インフラを構築（初回のみ）

```bash
export GITHUB_ORG=Amadeus-000
export GITHUB_REPO=sw-redirect-micro-service
export AWS_REGION=ap-northeast-1
bash scripts/bootstrap.sh
```

スクリプトが行うこと:

| ステップ | 内容 |
|----------|------|
| 1 | GitHub Actions 用 OIDC プロバイダーを AWS に登録 |
| 2 | Lambda 実行ロールを作成し `AWSLambdaBasicExecutionRole` をアタッチ |
| 3 | Lambda 関数と Function URL を初期作成 |
| 4 | GitHub Actions 用デプロイロールを作成（最小権限） |
| 5 | 登録すべき Secret の ARN を出力 |

> **Note**  
> OIDC プロバイダー (`token.actions.githubusercontent.com`) はアカウント内に 1 つしか作成できません。  
> 既に存在する場合はスクリプトが検出してスキップします。

### 2. GitHub Actions Secret を設定

 bootstrap.sh の出力値を GitHub リポジトリの Secret に登録します。

| Secret 名 | 値 |
|-----------|-----|
| `AWS_DEPLOY_ROLE_ARN` | bootstrap.sh が出力した ARN |

GitHub → **Settings → Secrets and variables → Actions → New repository secret**

### 3. main ブランチへ push

```bash
git push origin main
```

`deploy.yml` が起動し Lambda が自動更新されます。

## ワークフロー概要

```
push to main
  └─ deploy.yml
        ├─ OIDC で AWS 認証
        ├─ src/handler.py を zip
        ├─ lambda:UpdateFunctionCode
        ├─ function-updated 待機
        └─ Function URL へ curl スモークテスト
```

### OIDC 認証フロー

```
GitHub Actions Runner
  │
  ├─ OIDC トークン発行 (id-token: write)
  │
  └─► AWS STS AssumeRoleWithWebIdentity
        └─► IAM Role: sw-redirect-hello-world-github-actions-role
              ├─ 許可: repo:Amadeus-000/sw-redirect-micro-service のみ
              └─ 権限: lambda:UpdateFunctionCode / GetFunction のみ
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