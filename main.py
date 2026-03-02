from src.handler import lambda_handler
from aws_lambda_typing import context as context_

def main():
    print("Hello from sw-redirect-micro-service!")


if __name__ == "__main__":
    main()
    lambda_handler({}, context_.Context())
