FROM python:3.7.0

RUN mkdir /mlflow/

RUN pip install --no-cache-dir boto3 pymysql mlflow

EXPOSE 5000

# ENV MLFLOW_S3_ENDPOINT_URL=http://127.0.0.1:9000/
# ENV AWS_ACCESS_KEY_ID=minio
# ENV AWS_SECRET_ACCESS_KEY=minio123

CMD mlflow server \
    --host 0.0.0.0 \
    --backend-store-uri mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@${MYSQL_HOST}:3306/${MYSQL_DATABASE} \
    --default-artifact-root s3://${BUCKET}
