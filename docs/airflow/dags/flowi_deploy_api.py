import json
import os
import time
import uuid
from datetime import datetime, timedelta
from pprint import pprint

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from os import path
import yaml
from kubernetes import client, config
from utils.mongo import Mongo


default_args = {
    "owner": "flowi",
    "depends_on_past": False,
    "start_date": datetime(2020, 3, 21),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG("FlowiDeployAPI", default_args=default_args, catchup=False, schedule_interval=None)


docker_build_task = BashOperator(
    task_id="docker_build",
    bash_command="/usr/local/airflow/dags/deploy/docker_build_api.sh '{{ dag_run.conf[\"flow_name\"] }}' '{{ dag_run.conf[\"run_id\"] }}' ",
    dag=dag,
)


def deploy_seldon(name: str, group: str, plural: str, version: str, yaml_content: str):
    config.load_incluster_config()
    namespace = "seldon"

    body = yaml.safe_load(yaml_content)

    api = client.CustomObjectsApi()
    try:
        resource = api.get_namespaced_custom_object(
            group=group, version=version, plural=plural, namespace=namespace, name=name
        )
        print("Deployment already exists")

        if "drift" in name:
            resource = api.delete_namespaced_custom_object(
                group=group, version=version, plural=plural, namespace=namespace, name=name
            )
            print("Deleting deployment")
            # print(resource)
            time.sleep(5)

            resource = api.create_namespaced_custom_object(
                group=group, version=version, plural=plural, namespace=namespace, body=body
            )
            print("Creating deployment")
            print(resource)
        else:
            resource = api.patch_namespaced_custom_object(
                group=group, version=version, plural=plural, namespace=namespace, name=name, body=body
            )
            print("Resource updated details:")
            pprint(resource)

    except Exception:
        resource = api.create_namespaced_custom_object(
            group=group, version=version, plural=plural, namespace=namespace, body=body
        )
        print("Creating deployment")
        print(resource)


def deploy_api_model(ds, **kwargs):
    group = "machinelearning.seldon.io"
    plural = "seldondeployments"
    flow_name = kwargs["dag_run"].conf["flow_name"]
    version = "v1"
    name = flow_name

    yaml_content = f"""
    apiVersion: machinelearning.seldon.io/v1
    kind: SeldonDeployment
    metadata:
      name: {name}
      namespace: seldon
    spec:
      name: {name}
      predictors:
      - componentSpecs:
        - spec:
            containers:
            - name: classifier
              image: localhost:32000/flowi-{flow_name}
              imagePullPolicy: Always
        graph:
          children: []
          endpoint:
            type: REST
          name: classifier
          type: MODEL
          logger:
            url: http://broker-ingress.knative-eventing.svc.cluster.local/seldon/default
            mode: all
        name: {flow_name}
        replicas: 1
        """

    deploy_seldon(name=name, group=group, plural=plural, version=version, yaml_content=yaml_content)


deploy_api_model_task = PythonOperator(
    task_id="deploy_api_model", provide_context=True, python_callable=deploy_api_model, dag=dag
)


def deploy_drift_detector(ds, **kwargs):
    group = "serving.knative.dev"
    plural = "services"
    flow_name = kwargs["dag_run"].conf["flow_name"]
    version = "v1"
    run_id = kwargs["dag_run"].conf["run_id"]
    name = f"drift-detector-{flow_name}"

    yaml_content = f"""
    apiVersion: serving.knative.dev/v1
    kind: Service
    metadata:
      name: {name}
      namespace: seldon
    spec:
      template:
        metadata:
          annotations:
            autoscaling.knative.dev/minScale: "1"
        spec:
          containers:
          - image: seldonio/alibi-detect-server:1.11.2
            env:
              - name: RCLONE_CONFIG_S3_TYPE
                value: s3
              - name: RCLONE_CONFIG_S3_PROVIDER
                value: minio
              - name: RCLONE_CONFIG_S3_ENV_AUTH
                value: "false"
              - name: RCLONE_CONFIG_S3_ENDPOINT
                value: {os.environ["MLFLOW_S3_ENDPOINT_URL"]}
              - name: RCLONE_CONFIG_S3_ACCESS_KEY_ID
                value: {os.environ["AWS_ACCESS_KEY_ID"]}
              - name: RCLONE_CONFIG_S3_SECRET_ACCESS_KEY
                value: {os.environ["AWS_SECRET_ACCESS_KEY"]}
            imagePullPolicy: IfNotPresent
            args:
            - --model_name
            - {flow_name}dd
            - --http_port
            - '8080'
            - --protocol
            - seldon.http
            - --storage_uri
            - s3://models/staging/{run_id}
            - --reply_url
            - http://message-dumper.seldon
            - --event_type
            - io.seldon.serving.inference.drift
            - --event_source
            - io.seldon.serving.{flow_name}dd
            - DriftDetector
            - --drift_batch_size
            - '500'
    """

    deploy_seldon(name=name, group=group, plural=plural, version=version, yaml_content=yaml_content)


deploy_drift_detector_task = PythonOperator(
    task_id="deploy_drift_detector", provide_context=True, python_callable=deploy_drift_detector, dag=dag
)


def deploy_drift_trigger(ds, **kwargs):
    group = "eventing.knative.dev"
    plural = "triggers"
    flow_name = kwargs["dag_run"].conf["flow_name"]
    version = "v1"
    name = f"drift-trigger-{flow_name}"

    yaml_content = f"""
    apiVersion: eventing.knative.dev/v1
    kind: Trigger
    metadata:
      name: {name}
      namespace: seldon
    spec:
      broker: default
      filter:
        attributes:
          type: io.seldon.serving.inference.request
      subscriber:
        ref:
          apiVersion: serving.knative.dev/v1
          kind: Service
          name: drift-detector-{flow_name}
    """

    deploy_seldon(name=name, group=group, plural=plural, version=version, yaml_content=yaml_content)


deploy_drift_trigger_task = PythonOperator(
    task_id="deploy_drift_trigger", provide_context=True, python_callable=deploy_drift_trigger, dag=dag
)


docker_build_task.set_downstream(deploy_api_model_task)
deploy_api_model_task.set_downstream(deploy_drift_detector_task)
deploy_drift_detector_task.set_downstream(deploy_drift_trigger_task)
