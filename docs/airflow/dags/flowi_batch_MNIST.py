import json
import os
import uuid
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators import kubernetes_pod
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from kubernetes.client import models as k8s
from utils.validate_flow import ValidateFlow
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


dag = DAG("FlowiBatchMNIST", default_args=default_args, catchup=False, schedule_interval=None)
flowi_configs_path = "dags/flowi_configs/"
flow_name = "MNIST"

with open(os.path.join(flowi_configs_path, "flowi_config_MNIST.json"), "r") as json_file:
    flowi_config = json.load(json_file)

source = flowi_config["deploy"]["batch"]["source"]
destiny = flowi_config["deploy"]["batch"]["destiny"]


batch_task = kubernetes_pod.KubernetesPodOperator(
    dag=dag,
    namespace="flowi",
    image=f"localhost:32000/flowi-batch-{flow_name.lower()}:latest",
    image_pull_policy="Always",
    cmds=["python"],
    arguments=["-m", "flowi", "predict", "--source", json.dumps(source), "--destiny", json.dumps(destiny)],
    name=f"flowi-batch-{flow_name.lower()}",
    env_vars=[
        k8s.V1EnvVar(name="FLOW_NAME", value=flow_name),
        k8s.V1EnvVar(name="DASK_SCHEDULER", value="tcp://dask-scheduler:8786"),
        k8s.V1EnvVar(name="MLFLOW_S3_ENDPOINT_URL", value=os.environ["MLFLOW_S3_ENDPOINT_URL"]),
        k8s.V1EnvVar(name="FLOWI_BUCKET", value="flowi"),
        k8s.V1EnvVar(name="AWS_ACCESS_KEY_ID", value=os.environ["AWS_ACCESS_KEY_ID"]),
        k8s.V1EnvVar(name="AWS_SECRET_ACCESS_KEY", value=os.environ["AWS_SECRET_ACCESS_KEY"]),
    ],
    is_delete_operator_pod=True,
    in_cluster=True,
    task_id="flowi-batch",
    do_xcom_push=True,
    get_logs=True,
)


def get_branch_follow(**kwargs):
    x = kwargs["ti"].xcom_pull(task_ids="flowi-batch", key="drift")
    print("From Kwargs: ", x)
    if x == "1":
        return "task_drifted"
    else:
        return "task_not_drifted"


task_branch = BranchPythonOperator(
    task_id="task_branch", python_callable=get_branch_follow, provide_context=True, dag=dag
)

task_drifted = BashOperator(bash_command="echo Drifted!", task_id="task_drifted", dag=dag)

task_not_drifted = BashOperator(bash_command="echo Not Drifted!", task_id="task_not_drifted", dag=dag)


# batch_task >> task_branch
batch_task.set_downstream(task_branch)

# task_branch >> task_drifted
task_branch.set_downstream(task_drifted)

# task_branch >> task_not_drifted
task_branch.set_downstream(task_not_drifted)
