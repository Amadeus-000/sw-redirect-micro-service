import os
import json
import requests
from aws_lambda_typing import context as context_
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.responses import APIGatewayProxyResponseV2



def lambda_handler(event: APIGatewayProxyEventV2, context: context_.Context) -> APIGatewayProxyResponseV2:
    path = event.get('rawPath', '/')
    if path == "/redirect":
        return handle_redirect(event, context)
    if path == "redirect-test":
        return handle_redirect(event, context)
    if path == "/test":
        redirect_url=fetch_redirect_url("google")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"redirect_url: {redirect_url}"}),
        }
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


def fetch_redirect_url(work_id: str)-> str|None:
    API_KEY = os.environ.get("MICRO_CMS_API_KEY")
    if not API_KEY:
        raise ValueError("MICRO_CMS_API_KEY environment variable is not set")
    response = requests.get(
        url ="https://sw-app.microcms.io/api/v1/redirect", 
        headers={
            "X-MICROCMS-API-KEY": API_KEY,
        },
            params={
            "filters": f"work_id[equals]{work_id}",
            "limit": 1,
        }
    )
    response.raise_for_status()
    data = response.json()
    return data[0]["redirect_url"] if data else None