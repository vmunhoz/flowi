from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from kubernetes.client import models as k8s
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.providers.cncf.kubernetes.operators import spark_kubernetes
import uuid
import re

# Following are defaults which can be overridden later on
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

dag = DAG("FlowiTrain", default_args=default_args, catchup=False, schedule_interval="@daily")


def create_spark_app_yaml(**kwargs):
    ti = kwargs["ti"]
    spark_app = kwargs["spark_app"]

    flowi_run_uuid = str(uuid.uuid4())

    print("flowi_run_name: {}".format(flowi_run_uuid))

    file_path = f"/usr/local/airflow/dags/{spark_app}_spark_application.yaml"
    with open(file_path, "r") as f:
        file_content = f.read()

    file_content = re.sub(
        r"\b[0-9a-f]{8}\b-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-\b[0-9a-f]{12}\b", flowi_run_uuid, file_content
    )

    with open(file_path, "w") as f:
        f.write(file_content)

    ti.xcom_push("flowi_run_uuid", flowi_run_uuid)


def wait_preprocessing_yaml(**kwargs):
    from kubernetes import client, config
    import time

    ti = kwargs["ti"]
    spark_app = kwargs["spark_app"]
    upstream_task = kwargs["upstream_task"]

    flowi_run_uuid = ti.xcom_pull(task_ids=upstream_task, key="flowi_run_uuid")
    print(f"waiting {spark_app}: {flowi_run_uuid}")

    config.load_kube_config()
    v1 = client.CoreV1Api()

    count = 0
    max_retries = 4
    while count < max_retries:
        time.sleep(5)
        ret = v1.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            pod_name = i.metadata.name
            if pod_name.startswith(f"flowi-{spark_app}-") and flowi_run_uuid in pod_name:
                print("Waiting {}\t{}\t{}".format(i.status.pod_ip, i.metadata.namespace, i.metadata.name))
                count = 0
        else:
            print(f"No {spark_app} pod found")
            count += 1

    print("Done waiting!")


create_preprocessing_yaml_task = PythonOperator(
    task_id="create_preprocessing_yaml",
    dag=dag,
    python_callable=create_spark_app_yaml,
    provide_context=True,
    op_kwargs={"spark_app": "preprocessing"},
)

running_preprocessing_task = spark_kubernetes.SparkKubernetesOperator(
    application_file="preprocessing_spark_application.yaml", task_id="running_preprocessing", dag=dag
)


wait_preprocessing_task = PythonOperator(
    task_id="wait_preprocessing",
    dag=dag,
    python_callable=wait_preprocessing_yaml,
    provide_context=True,
    op_kwargs={"spark_app": "preprocessing", "upstream_task": "create_preprocessing_yaml"},
)

create_training_yaml_task = PythonOperator(
    task_id="create_training_yaml",
    dag=dag,
    python_callable=create_spark_app_yaml,
    provide_context=True,
    op_kwargs={"spark_app": "training"},
)

running_training_task = spark_kubernetes.SparkKubernetesOperator(
    application_file="training_spark_application.yaml", task_id="running_training", dag=dag
)

wait_training_task = PythonOperator(
    task_id="wait_training",
    dag=dag,
    python_callable=wait_preprocessing_yaml,
    provide_context=True,
    op_kwargs={"spark_app": "training", "upstream_task": "create_training_yaml"},
)


# Preprocessing
running_preprocessing_task.set_upstream(create_preprocessing_yaml_task)
wait_preprocessing_task.set_upstream(running_preprocessing_task)

# Training
create_training_yaml_task.set_upstream(wait_preprocessing_task)
running_training_task.set_upstream(create_training_yaml_task)
wait_training_task.set_upstream(running_training_task)
