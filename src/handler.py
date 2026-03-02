import json

from aws_lambda_typing import context as context_
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.responses import APIGatewayProxyResponseV2


def lambda_handler(event: APIGatewayProxyEventV2, context: context_.Context) -> APIGatewayProxyResponseV2:
    path = event.get('rawPath', '/')
    query_params = event.get('queryStringParameters', {}) or {}
    work_id = query_params.get('work_id')

    if not work_id:
        work_id = "No work_id provided"
    
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json",
        },
        "body": json.dumps({"message": "Hello, World!", "path": path, "work_id": work_id}),
    }

