import json
import logging

from aws_lambda_typing import context as context_
from aws_lambda_typing.events import APIGatewayProxyEventV2
from aws_lambda_typing.responses import APIGatewayProxyResponseV2

from libs.crypto import decrypt
from services.micro_cms import fetch_redirect_url

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: APIGatewayProxyEventV2, context: context_.Context) -> APIGatewayProxyResponseV2:
   path = (event.get("rawPath") or event.get("path") or "").strip("/") or ""
   logger.info(f"Received request for path: {path}")
   if path == "redirect":
      return handle_redirect(event, context)
   if path == "test":
      redirect_url = fetch_redirect_url("google")
      return {
         "statusCode": 200,
         "headers": {"Content-Type": "application/json"},
         "body": json.dumps({"message": f"redirect_url: {redirect_url}"}),
      }
   return {
      "statusCode": 200,
      "body": "fail redirect",
   }


def handle_redirect(event: APIGatewayProxyEventV2, context: context_.Context) -> APIGatewayProxyResponseV2:
   try:
      query_params = event.get("queryStringParameters", {}) or {}
      encrypted_id = query_params.get("id") or ""

      if not encrypted_id:
         logger.error("Error: id parameter is missing")
         return {
            "statusCode": 400,
            "body": json.dumps({"error": "id parameter is required"}),
         }

      logger.info(f"Encrypted ID: {encrypted_id}")
      work_id = decrypt(encrypted_id)
      logger.info(f"Decrypted work_id: {work_id}")

      redirect_url = fetch_redirect_url(work_id)
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
