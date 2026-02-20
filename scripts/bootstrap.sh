#!/usr/bin/env bash
# ============================================================
# bootstrap.sh
# 初回セットアップ: OIDC プロバイダー登録 + IAM ロール作成
#                   + Lambda 実行ロール + Lambda 関数初期作成
#
# 使い方:
#   export GITHUB_ORG=Amadeus-000
#   export GITHUB_REPO=sw-redirect-micro-service
#   export AWS_REGION=ap-northeast-1
#   bash scripts/bootstrap.sh
# ============================================================
set -euo pipefail

# ─── 設定 ────────────────────────────────────────────────────
GITHUB_ORG="${GITHUB_ORG:?GITHUB_ORG を設定してください}"
GITHUB_REPO="${GITHUB_REPO:?GITHUB_REPO を設定してください}"
AWS_REGION="${AWS_REGION:-ap-northeast-1}"
FUNCTION_NAME="${FUNCTION_NAME:-sw-redirect-hello-world}"
DEPLOY_ROLE_NAME="${FUNCTION_NAME}-github-actions-role"
EXEC_ROLE_NAME="${FUNCTION_NAME}-exec-role"
OIDC_URL="https://token.actions.githubusercontent.com"
OIDC_AUDIENCE="sts.amazonaws.com"

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Account: ${AWS_ACCOUNT_ID}  Region: ${AWS_REGION}"

# ─── 1. GitHub Actions OIDC プロバイダー登録 ──────────────────
echo ""
echo "==> [1/5] OIDC プロバイダーを確認・作成"

OIDC_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/token.actions.githubusercontent.com"

if aws iam get-open-id-connect-provider --open-id-connect-provider-arn "${OIDC_ARN}" \
     > /dev/null 2>&1; then
  echo "    既存の OIDC プロバイダーを使用します: ${OIDC_ARN}"
else
  # GitHub の thumbprint を取得
  THUMBPRINT=$(openssl s_client -connect token.actions.githubusercontent.com:443 \
    -showcerts </dev/null 2>/dev/null \
    | awk '/-----BEGIN CERTIFICATE-----/{p=1;cert=""} p{cert=cert $0 "\n"} /-----END CERTIFICATE-----/{last=cert; p=0} END{print last}' \
    | openssl x509 -fingerprint -noout -sha1 2>/dev/null \
    | sed 's/.*=//;s/://g' | tr '[:upper:]' '[:lower:]')

  aws iam create-open-id-connect-provider \
    --url "${OIDC_URL}" \
    --client-id-list "${OIDC_AUDIENCE}" \
    --thumbprint-list "${THUMBPRINT}"
  echo "    OIDC プロバイダーを作成しました: ${OIDC_ARN}"
fi

# ─── 2. Lambda 実行ロール ─────────────────────────────────────
echo ""
echo "==> [2/5] Lambda 実行ロールを確認・作成: ${EXEC_ROLE_NAME}"

EXEC_TRUST_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Service": "lambda.amazonaws.com"},
    "Action": "sts:AssumeRole"
  }]
}
EOF
)

if aws iam get-role --role-name "${EXEC_ROLE_NAME}" > /dev/null 2>&1; then
  echo "    既存の実行ロールを使用します"
  EXEC_ROLE_ARN=$(aws iam get-role --role-name "${EXEC_ROLE_NAME}" \
    --query 'Role.Arn' --output text)
else
  EXEC_ROLE_ARN=$(aws iam create-role \
    --role-name "${EXEC_ROLE_NAME}" \
    --assume-role-policy-document "${EXEC_TRUST_POLICY}" \
    --query 'Role.Arn' --output text)
  aws iam attach-role-policy \
    --role-name "${EXEC_ROLE_NAME}" \
    --policy-arn "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  echo "    実行ロールを作成しました: ${EXEC_ROLE_ARN}"
  # ロールが伝播するまで待機
  echo "    IAM ロールの伝播を待機中 (10s)..."
  sleep 10
fi

# ─── 3. Lambda 関数の初期作成 ─────────────────────────────────
echo ""
echo "==> [3/5] Lambda 関数を確認・作成: ${FUNCTION_NAME}"

# 一時 zip を作成
TMPDIR_ZIP=$(mktemp -d)
zip -j "${TMPDIR_ZIP}/lambda.zip" src/handler.py > /dev/null

if aws lambda get-function --function-name "${FUNCTION_NAME}" \
     --region "${AWS_REGION}" > /dev/null 2>&1; then
  echo "    既存の Lambda 関数を使用します"
else
  aws lambda create-function \
    --function-name "${FUNCTION_NAME}" \
    --runtime python3.12 \
    --handler handler.lambda_handler \
    --role "${EXEC_ROLE_ARN}" \
    --zip-file "fileb://${TMPDIR_ZIP}/lambda.zip" \
    --timeout 10 \
    --memory-size 128 \
    --region "${AWS_REGION}" \
    > /dev/null
  echo "    Lambda 関数を作成しました"

  # Function URL を有効化
  aws lambda create-function-url-config \
    --function-name "${FUNCTION_NAME}" \
    --auth-type NONE \
    --region "${AWS_REGION}" \
    > /dev/null
  FUNCTION_URL=$(aws lambda get-function-url-config \
    --function-name "${FUNCTION_NAME}" \
    --region "${AWS_REGION}" \
    --query 'FunctionUrl' --output text)
  echo "    Function URL: ${FUNCTION_URL}"
fi

rm -rf "${TMPDIR_ZIP}"

# ─── 4. GitHub Actions デプロイロール ────────────────────────
echo ""
echo "==> [4/5] GitHub Actions デプロイロールを確認・作成: ${DEPLOY_ROLE_NAME}"

FUNCTION_ARN="arn:aws:lambda:${AWS_REGION}:${AWS_ACCOUNT_ID}:function:${FUNCTION_NAME}"

DEPLOY_TRUST_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": {"Federated": "${OIDC_ARN}"},
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "${OIDC_AUDIENCE}"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub":
          "repo:${GITHUB_ORG}/${GITHUB_REPO}:ref:refs/heads/main"
      }
    }
  }]
}
EOF
)

DEPLOY_POLICY=$(cat <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Sid": "UpdateLambdaCode",
    "Effect": "Allow",
    "Action": [
      "lambda:UpdateFunctionCode",
      "lambda:GetFunction",
      "lambda:GetFunctionUrlConfig",
      "lambda:InvokeFunction"
    ],
    "Resource": "${FUNCTION_ARN}"
  }]
}
EOF
)

if aws iam get-role --role-name "${DEPLOY_ROLE_NAME}" > /dev/null 2>&1; then
  echo "    既存のデプロイロールを使用します"
  DEPLOY_ROLE_ARN=$(aws iam get-role --role-name "${DEPLOY_ROLE_NAME}" \
    --query 'Role.Arn' --output text)
  # trust policy を最新化
  aws iam update-assume-role-policy \
    --role-name "${DEPLOY_ROLE_NAME}" \
    --policy-document "${DEPLOY_TRUST_POLICY}"
else
  DEPLOY_ROLE_ARN=$(aws iam create-role \
    --role-name "${DEPLOY_ROLE_NAME}" \
    --assume-role-policy-document "${DEPLOY_TRUST_POLICY}" \
    --query 'Role.Arn' --output text)
  echo "    デプロイロールを作成しました: ${DEPLOY_ROLE_ARN}"
fi

# インラインポリシー適用
aws iam put-role-policy \
  --role-name "${DEPLOY_ROLE_NAME}" \
  --policy-name "${FUNCTION_NAME}-deploy-policy" \
  --policy-document "${DEPLOY_POLICY}"

# ─── 5. GitHub Actions Secrets に設定する値を出力 ────────────
echo ""
echo "==> [5/5] 完了! 以下の値を GitHub Actions Secrets に登録してください"
echo ""
echo "  Secret 名         値"
echo "  ────────────────  ────────────────────────────────────────────"
echo "  AWS_DEPLOY_ROLE_ARN  ${DEPLOY_ROLE_ARN}"
echo ""
echo "  GitHub → Settings → Secrets and variables → Actions"
echo "           → New repository secret"
