from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators import kubernetes_pod
from kubernetes.client import models as k8s

default_args = {
    'owner': 'leo',
    'depends_on_past': False,
    'start_date': datetime(2020, 3, 21),
    'email': ['psilva.leo@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag = DAG('FlowiTrainDask', default_args=default_args, catchup=False, schedule_interval='@daily')


volumes = [
    k8s.V1Volume(name='data-volume', host_path=k8s.V1HostPathVolumeSource(path='/tmp/flowi', type='DirectoryOrCreate'))
]

volume_mounts = [
    k8s.V1VolumeMount(mount_path='/data', sub_path=None, name='data-volume')
]

kubernetes_pod.KubernetesPodOperator(
    dag=dag,
    namespace='flowi',
    image='localhost:32000/flowi-preprocessing:latest',
    image_pull_policy='Always',
    # cmds=["sh", "-c", "mkdir -p /airflow/xcom/;echo '[1,2,3,4]' > /airflow/xcom/return.json"],
    name="preprocessing-dask",
    env_vars=[k8s.V1EnvVar(name='RUN_ID', value='test123')],
    volume_mounts=volume_mounts,
    volumes=volumes,
    is_delete_operator_pod=True,
    in_cluster=True,
    task_id="preprocessing-dask-master",
    get_logs=True
)
