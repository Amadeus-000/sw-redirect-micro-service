FROM public.ecr.aws/lambda/python:3.12

# 作業ディレクトリを設定
WORKDIR ${LAMBDA_TASK_ROOT}

# requirements.txtをコピーして依存関係をインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードをコピー
COPY src/ ${LAMBDA_TASK_ROOT}/

# Lambdaハンドラーを指定（handler.pyのlambda_handler関数を使用）
CMD [ "handler.lambda_handler" ]