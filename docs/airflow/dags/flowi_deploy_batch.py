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
from utils.mongo import Mongo

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

dag = DAG("FlowiDeployBatch", default_args=default_args, catchup=False, schedule_interval=None)
flowi_configs_path = "dags/flowi_configs/"


docker_build_task = BashOperator(
    task_id="docker_build",
    bash_command="/usr/local/airflow/dags/deploy/docker_build_batch.sh '{{ dag_run.conf[\"flow_name\"].lower() }}' '{{ dag_run.conf[\"run_id\"] }}' ",
    dag=dag,
)


def deploy_batch_model(ds, **kwargs):
    schedule_interval = kwargs["dag_run"].conf["schedule_interval"]
    schedule_interval = schedule_interval if schedule_interval == "None" else f"'{schedule_interval}'"

    flow_name = kwargs["dag_run"].conf["flow_name"]

    lines = open(os.path.join(flowi_configs_path, "flowi_batch.template"), "r").readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].replace("{{FLOW_NAME}}", flow_name)
        lines[i] = lines[i].replace("{{SCHEDULE_INTERVAL}}", schedule_interval)
    with open(os.path.join("dags/", f"flowi_batch_{flow_name}.py"), "w") as out_file:
        out_file.writelines(lines)


deploy_batch_model_task = PythonOperator(
    task_id="deploy_batch_model", provide_context=True, python_callable=deploy_batch_model, dag=dag
)


deploy_batch_model_task.set_upstream(docker_build_task)
