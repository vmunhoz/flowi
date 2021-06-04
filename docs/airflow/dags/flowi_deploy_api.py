import json
import os
import uuid
from datetime import datetime, timedelta
from pprint import pprint

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from os import path
import yaml
from kubernetes import client, config

# from kubernetes.client.exceptions import ApiException


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
    bash_command="/usr/local/airflow/dags/deploy/docker_build.sh '{{ dag_run.conf[\"flow_name\"] }}' ",
    dag=dag,
)


def deploy_api_model(ds, **kwargs):
    config.load_incluster_config()
    flow_name = kwargs["dag_run"].conf["flow_name"]
    group = "machinelearning.seldon.io"
    version = "v1"
    plural = "seldondeployments"
    namespace = "seldon"

    deployment = f"""
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: {flow_name}
  namespace: seldon
spec:
  name: {flow_name}
  predictors:
  - componentSpecs:
    - spec:
        containers:
        - name: classifier
          image: localhost:32000/flowi-{flow_name}
    graph:
      children: []
      endpoint:
        type: REST
      name: classifier
      type: MODEL
    name: {flow_name}
    replicas: 1
    """
    # with open(path.join(path.dirname(__file__), "seldon-deployment.yml")) as f:
    #     body = yaml.safe_load(f)
    body = yaml.safe_load(deployment)

    api = client.CustomObjectsApi()
    try:
        resource = api.get_namespaced_custom_object(
            group=group, version=version, plural=plural, namespace=namespace, name=flow_name
        )
        print("Deployment already exists")

        resource = api.patch_namespaced_custom_object(
            group=group, version=version, plural=plural, namespace=namespace, name=flow_name, body=body
        )
        print("Resource updated details:")
        pprint(resource)
    except Exception:
        resource = api.create_namespaced_custom_object(
            group=group, version=version, plural=plural, namespace=namespace, body=body
        )
        print("Creating deployment")
        print(resource)


deploy_api_model_task = PythonOperator(
    task_id="deploy_api_model_task", provide_context=True, python_callable=deploy_api_model, dag=dag
)

deploy_api_model_task.set_upstream(docker_build_task)
