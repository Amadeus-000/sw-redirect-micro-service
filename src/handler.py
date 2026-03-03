import json

from aws_lambda_typing import context as context_
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.responses import APIGatewayProxyResponseV2

from libs.crypto import decrypt, encrypt
from services.micro_cms import fetch_redirect_url


def lambda_handler(
    event: APIGatewayProxyEventV2, context: context_.Context
) -> APIGatewayProxyResponseV2:
    path = path = event.get("rawPath") or event.get("path") or "/"
    print(f"Received request for path: {path}")
    if path == "/redirect":
        return handle_redirect(event, context)
    if path == "/encrypt-id":
        return handle_encrypt_id(event, context)
    if path == "/test":
        redirect_url = fetch_redirect_url("google")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"redirect_url: {redirect_url}"}),
        }
    return {
        "statusCode": 302,
        "headers": {
            "Location": "TODO: sw-url",
        },
        "body": "default redirect",
    }


def handle_redirect(
    event: APIGatewayProxyEventV2, context: context_.Context
) -> APIGatewayProxyResponseV2:
    query_params = event.get("queryStringParameters", {}) or {}
    id = query_params.get("id") or ""
    work_id = decrypt(id)
    redirect_url = fetch_redirect_url(work_id)
    if not redirect_url:
        return {
            "statusCode": 302,
            "headers": {
                "Location": "https://google.com",
            },
            "body": "",
        }
    return {
        "statusCode": 302,
        "headers": {
            "Location": redirect_url,
        },
        "body": f"Redirecting to {redirect_url}",
    }


def handle_encrypt_id(
    event: APIGatewayProxyEventV2, context: context_.Context
) -> APIGatewayProxyResponseV2:
    try:
        body = event.get("body", "{}")
        data = json.loads(body) if body else {}
        work_id = data.get("work_id", "")

        if not work_id:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "work_id is required"}),
            }

        encrypted_id = encrypt(work_id)
        return {
            "statusCode": 200,
            "body": json.dumps({"id": encrypted_id}),
        }
    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON"}),
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)}),
        }
