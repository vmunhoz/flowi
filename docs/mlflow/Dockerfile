FROM python:3.9-slim-bullseye

RUN mkdir /mlflow/

RUN pip install --no-cache-dir boto3 pymysql mlflow

EXPOSE 5000

CMD sleep 10 && mlflow server \
    --host 0.0.0.0 \
    --port 5000 \
    --backend-store-uri mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}:3306/${MYSQL_DATABASE} \
    --default-artifact-root s3://${BUCKET}
