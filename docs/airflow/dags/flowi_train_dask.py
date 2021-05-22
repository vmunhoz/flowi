import json
import os
import uuid
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators import kubernetes_pod
from airflow.operators.python_operator import PythonOperator
from kubernetes.client import models as k8s

default_args = {
    "owner": "leo",
    "depends_on_past": False,
    "start_date": datetime(2020, 3, 21),
    "email": ["psilva.leo@gmail.com"],
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

dag = DAG("FlowiTrainDask", default_args=default_args, catchup=False, schedule_interval="@daily")
flowi_run_id = str(uuid.uuid4())
flow_name = "Iris"


def run_this_func(ds, **kwargs):
    print("Remotely received value of {}".format(json.dumps(kwargs["dag_run"].conf["flow_chart"])))


run_this = PythonOperator(task_id="run_this", provide_context=True, python_callable=run_this_func, dag=dag)


train_task = kubernetes_pod.KubernetesPodOperator(
    dag=dag,
    namespace="flowi",
    image="localhost:32000/flowi:latest",
    image_pull_policy="Always",
    cmds=["python"],
    arguments=["-m", "flowi", "--chart", "{{ dag_run.conf['flow_chart'] }}"],
    name="flowi-train",
    env_vars=[
        k8s.V1EnvVar(name="RUN_ID", value=flowi_run_id),
        k8s.V1EnvVar(name="FLOW_NAME", value=flow_name),
        k8s.V1EnvVar(name="VERSION", value="{{ dag_run.conf['version'] }}"),
        k8s.V1EnvVar(name="EXPERIMENT_TRACKING", value="{{ dag_run.conf['experiment_tracking'] }}"),
        k8s.V1EnvVar(name="MLFLOW_S3_ENDPOINT_URL", value=os.environ["MLFLOW_S3_ENDPOINT_URL"]),
        k8s.V1EnvVar(name="FLOWI_BUCKET", value="flowi"),
        k8s.V1EnvVar(name="MONGO_ENDPOINT_URL", value="mongo-service"),
        k8s.V1EnvVar(name="DASK_SCHEDULER", value="dask-scheduler"),
        k8s.V1EnvVar(name="MLFLOW_TRACKING_URI", value="http://mlflow-service"),
        k8s.V1EnvVar(name="AWS_ACCESS_KEY_ID", value=os.environ["AWS_ACCESS_KEY_ID"]),
        k8s.V1EnvVar(name="AWS_SECRET_ACCESS_KEY", value=os.environ["AWS_SECRET_ACCESS_KEY"]),
    ],
    is_delete_operator_pod=True,
    in_cluster=True,
    task_id="flowi-train",
    get_logs=True,
)

train_task.set_upstream(run_this)
