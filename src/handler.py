import json
import logging

from aws_lambda_typing import context as context_
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.responses import APIGatewayProxyResponseV2

from services.micro_cms import fetch_redirect_url

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: APIGatewayProxyEventV2, context: context_.Context) -> APIGatewayProxyResponseV2:
   path = (event.get("rawPath") or event.get("path") or "").strip("/") or ""
   if path == "redirect":
      return handle_redirect(event, context)
   if path == "test":
      redirect_url = fetch_redirect_url("b9sjmr7tjks")  # Google.comへのリダイレクトURLを取得するテストコード
      return {
         "statusCode": 200,
         "headers": {"Content-Type": "application/json"},
         "body": json.dumps({"message": f"redirect_url: {redirect_url}"}),
      }
   return {
      "statusCode": 200,
      "headers": {"content-type": "application/json"},
      "body": json.dumps(
         {
            "message": "Hello from sphereworld.org!",
            # "rawPath": event.get("rawPath"),
            # "stage": event.get("requestContext", {}).get("stage"),
            # "httpPath": event.get("requestContext", {}).get("http", {}).get("path"),
            # "routeKey": event.get("routeKey"),
         }
      ),
   }


def handle_redirect(event: APIGatewayProxyEventV2, context: context_.Context) -> APIGatewayProxyResponseV2:
   try:
      query_params = event.get("queryStringParameters", {}) or {}
      id = query_params.get("id") or ""

      if not id:
         logger.error("Error: id parameter is missing")
         return {
            "statusCode": 400,
            "body": json.dumps({"error": "id parameter is required"}),
         }

      redirect_url = fetch_redirect_url(id)
      logger.info(f"Redirect URL: {redirect_url}")

      if not redirect_url:
         return {
            "statusCode": 302,
            "headers": {
               "Location": "https://sphereworld.org/404",
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
   except Exception as e:
      logger.error(f"Error in handle_redirect: {str(e)}")
      return {
         "statusCode": 500,
         "body": json.dumps({"error": f"Failed to process redirect: {str(e)}"}),
      }
