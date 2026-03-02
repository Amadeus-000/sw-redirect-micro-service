import json

from aws_lambda_typing import context as context_
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.responses import APIGatewayProxyResponseV2


def lambda_handler(event: APIGatewayProxyEventV2, context: context_.Context) -> APIGatewayProxyResponseV2:
    path = event.get('rawPath', '/')
    if path == "/redirect":
        return handle_redirect(event, context)
    if path == "redirect-test":
        return handle_redirect(event, context)
    return {
            "statusCode": 302,
            "headers": {
                "Location": "TODO: sw-url",
            },
            "body": "",
        }

def handle_redirect_test(event: APIGatewayProxyEventV2, context: context_.Context) -> APIGatewayProxyResponseV2:
    query_params = event.get('queryStringParameters', {}) or {}
    work_id = query_params.get('work_id')

    if not work_id:
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "work_id is required"}),
        }
    
    redirect_url = f"https://example.com/works/{work_id}"
    
    return {
        "statusCode": 200,
        "headers": {
            "Location": redirect_url,
        },
        "body": f"Redirecting to {redirect_url}",
    }

def handle_redirect(event: APIGatewayProxyEventV2, context: context_.Context) -> APIGatewayProxyResponseV2:
    query_params = event.get('queryStringParameters', {}) or {}
    work_id = query_params.get('work_id')

    if not work_id:
        return {
            "statusCode": 302,
            "headers": {
                "Location": "TODO: sw-url",
            },
            "body": "",
        }
    
    redirect_url = f"https://example.com/works/{work_id}"
    
    return {
        "statusCode": 302,
        "headers": {
            "Location": redirect_url,
        },
        "body": f"Redirecting to {redirect_url}",
    }