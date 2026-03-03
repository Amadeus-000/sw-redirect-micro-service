#!/bin/bash
set -e

docker build -t sw-redirect-lambda .
docker run -d -p 9000:8080 --env-file .env sw-redirect-lambda
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{
    "httpMethod": "GET",
    "path": "'"${1:-/test}"'",
    "queryStringParameters": {
      "work_id": "'"${2:-test123}"'"
    }
  }'
docker logs $(docker ps -q)
docker stop $(docker ps -q)