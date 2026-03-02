#!/bin/bash
set -e

# TODO: 作りかけ
docker build -t sw-redirect-lambda .
docker run -d -p 9000:8080 sw-redirect-lambda
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{
    "httpMethod": "GET",
    "path": "/redirect-test",
    "queryStringParameters": {
      "work_id": "test123"
    }
  }'