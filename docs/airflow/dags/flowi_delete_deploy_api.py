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

dag = DAG("FlowiDeleteAPI", default_args=default_args, catchup=False, schedule_interval=None)


def deploy_seldon(name: str, group: str, plural: str, version: str):
    config.load_incluster_config()
    namespace = "seldon"

    api = client.CustomObjectsApi()
    try:
        print("Deleting deployment")
        api.delete_namespaced_custom_object(group=group, version=version, plural=plural, namespace=namespace, name=name)
        print("Deleted deployment")

    except Exception:
        print("Error deleting deployment")


def deploy_api_model(ds, **kwargs):
    group = "machinelearning.seldon.io"
    plural = "seldondeployments"
    flow_name = kwargs["dag_run"].conf["flow_name"]
    version = "v1"
    name = flow_name

    deploy_seldon(name=name, group=group, plural=plural, version=version)


deploy_api_model_task = PythonOperator(
    task_id="delete_deploy_api_model", provide_context=True, python_callable=deploy_api_model, dag=dag
)


def deploy_drift_detector(ds, **kwargs):
    group = "serving.knative.dev"
    plural = "services"
    flow_name = kwargs["dag_run"].conf["flow_name"]
    version = "v1"
    name = f"drift-detector-{flow_name}"

    deploy_seldon(name=name, group=group, plural=plural, version=version)


deploy_drift_detector_task = PythonOperator(
    task_id="delete_deploy_drift_detector", provide_context=True, python_callable=deploy_drift_detector, dag=dag
)


def deploy_drift_trigger(ds, **kwargs):
    group = "eventing.knative.dev"
    plural = "triggers"
    flow_name = kwargs["dag_run"].conf["flow_name"]
    version = "v1"
    name = f"drift-trigger-{flow_name}"

    deploy_seldon(name=name, group=group, plural=plural, version=version)


deploy_drift_trigger_task = PythonOperator(
    task_id="delete_deploy_drift_trigger", provide_context=True, python_callable=deploy_drift_trigger, dag=dag
)


deploy_api_model_task.set_downstream(deploy_drift_detector_task)
deploy_drift_detector_task.set_downstream(deploy_drift_trigger_task)
