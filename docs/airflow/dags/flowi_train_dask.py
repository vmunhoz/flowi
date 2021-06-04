import json
import os
import uuid
from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators import kubernetes_pod
from airflow.operators.python_operator import PythonOperator
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

dag = DAG("FlowiTrainDask", default_args=default_args, catchup=False, schedule_interval=None)
flowi_run_id = str(uuid.uuid4())
flow_name = "Iris"
deploy_api = True


def validate_chart_func(ds, **kwargs):
    chart = kwargs["dag_run"].conf["flow_chart"]
    print("Remotely chart! {}".format(chart))

    nodes = chart["nodes"]
    links = chart["links"]

    validate_flow = ValidateFlow(nodes=nodes)
    for link in links:
        from_node = links[link]["from"]["nodeId"]
        to_node = links[link]["to"]["nodeId"]
        validate_flow.add_edge(from_node=from_node, to_node=to_node)

    is_cyclic = validate_flow.is_cyclic()
    if is_cyclic:
        print("Graph is cyclic. Validation error.")
        raise ValueError("Graph must be acyclic. There must be no cycles in the flow chart.")
    else:
        print("Validated graph as not cyclic")


validate_chart_task = PythonOperator(
    dag=dag, task_id="validate_chart", provide_context=True, python_callable=validate_chart_func
)


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
        k8s.V1EnvVar(name="DASK_SCHEDULER", value="tcp://dask-scheduler:8786"),
        k8s.V1EnvVar(name="MLFLOW_TRACKING_URI", value="http://mlflow-service"),
        k8s.V1EnvVar(name="AWS_ACCESS_KEY_ID", value=os.environ["AWS_ACCESS_KEY_ID"]),
        k8s.V1EnvVar(name="AWS_SECRET_ACCESS_KEY", value=os.environ["AWS_SECRET_ACCESS_KEY"]),
    ],
    is_delete_operator_pod=True,
    in_cluster=True,
    task_id="flowi-train",
    get_logs=True,
)


def compare_models_func(ds, **kwargs):
    version = kwargs["dag_run"].conf["version"]
    print("Comparing models from mongo. FlowName {} | Version {}".format(flow_name, version))
    mongo = Mongo()
    models = mongo.get_models_by_version(flow_name=flow_name, version=version)
    best_model = None
    best_performance = 0.0
    for model in models:
        model_performance = model["metrics"]["accuracy"]
        if model_performance > best_performance:
            best_performance = model_performance
            best_model = model

    print(best_model)


compare_models = PythonOperator(
    task_id="compare_models", provide_context=True, python_callable=compare_models_func, dag=dag
)


train_task.set_upstream(validate_chart_task)
compare_models.set_upstream(train_task)

if deploy_api:
    trigger_deploy_api_task = TriggerDagRunOperator(
        dag=dag,
        task_id="trigger_deploy_api_task",
        trigger_dag_id="FlowiDeployAPI",  # Ensure this equals the dag_id of the DAG to trigger
        conf={"flow_name": "iris-model"},
    )

    trigger_deploy_api_task.set_upstream(compare_models)
