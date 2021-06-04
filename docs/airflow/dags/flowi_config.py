import json
import os
import uuid
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators import kubernetes_pod
from airflow.operators.python_operator import PythonOperator
from kubernetes.client import models as k8s


default_args = {
    "owner": "flowi",
    "depends_on_past": False,
    "start_date": datetime(2020, 3, 21),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG("FlowiConfig", default_args=default_args, catchup=False, schedule_interval=None)
flowi_configs_path = "dags/flowi_configs/"


def create_config_file(ds, **kwargs):
    schedule_interval = kwargs["dag_run"].conf["schedule_interval"]
    schedule_interval = schedule_interval if schedule_interval == "None" else f"'{schedule_interval}'"

    config = kwargs["dag_run"].conf
    config["schedule_interval"] = schedule_interval
    flow_name = config["flow_name"]

    with open(os.path.join(flowi_configs_path, f"flowi_config_{flow_name}.json"), "w") as json_file:
        json_file.write(json.dumps(config))

    lines = open(os.path.join(flowi_configs_path, "flowi_train.template"), "r").readlines()
    for i in range(len(lines)):
        lines[i] = lines[i].replace("{{FLOW_NAME}}", flow_name)
        lines[i] = lines[i].replace("{{SCHEDULE_INTERVAL}}", schedule_interval)
    with open(os.path.join("dags/", f"flowi_train_{flow_name}.py"), "w") as out_file:
        out_file.writelines(lines)


create_config_file_task = PythonOperator(
    dag=dag, task_id="create_config_file", provide_context=True, python_callable=create_config_file
)
