import uuid
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators import kubernetes_pod
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

volumes = [
    k8s.V1Volume(name="data-volume", host_path=k8s.V1HostPathVolumeSource(path="/tmp/flowi", type="DirectoryOrCreate"))
]

volume_mounts = [k8s.V1VolumeMount(mount_path="/data", sub_path=None, name="data-volume")]

kubernetes_pod.KubernetesPodOperator(
    dag=dag,
    namespace="flowi",
    image="localhost:32000/flowi:latest",
    image_pull_policy="Always",
    cmds=["flowi", "{{ dag_run.conf['flow_chart'] }}"],
    name="flowi-train",
    env_vars=[
        k8s.V1EnvVar(name="RUN_ID", value=flowi_run_id),
        k8s.V1EnvVar(name="FLOW_NAME", value=flow_name),
        k8s.V1EnvVar(name="VERSION", value="{{ dag_run.conf['version'] }}"),
        k8s.V1EnvVar(name="EXPERIMENT_TRACKING", value="{{ dag_run.conf['experiment_tracking'] }}"),
        k8s.V1EnvVar(name="MLFLOW_S3_ENDPOINT_URL", value="mlflow-service"),
        k8s.V1EnvVar(name="MONGO_ENDPOINT_URL", value="mongo-service"),
    ],
    volume_mounts=volume_mounts,
    volumes=volumes,
    is_delete_operator_pod=True,
    in_cluster=True,
    task_id="flowi-train",
    get_logs=True,
)
