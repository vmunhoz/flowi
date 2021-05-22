import json
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator

# from airflow.operators.docker_operator import DockerOperator
from datetime import datetime

from flow_chart.validate_flow import ValidateFlow

args = {"start_date": datetime(2020, 3, 21), "owner": "airflow"}

dag = DAG(dag_id="example_dag_conf", default_args=args, schedule_interval=None)


def run_this_func(ds, **kwargs):
    chart = kwargs["dag_run"].conf["chart"]
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
        print("Graph is cyclic")
        raise ValueError("Graph must be acyclic. There must be no cycles in the flow chart.")
    else:
        print("Graph is NOT cyclic")


validate_chart_task = PythonOperator(
    task_id="validate_chart", provide_context=True, python_callable=run_this_func, dag=dag
)


def create_chart(dag):
    dag_run = dag.get_dagrun(execution_date=dag.latest_execution_date)

    if dag_run is not None:
        return json.dumps(dag_run.conf["chart"])
    return ""


# train_task = DockerOperator(
#     task_id="train",
#     image="flowi-train",
#     api_version="auto",
#     auto_remove=True,
#     command="python main.py --chart '{}'".format(create_chart(dag)),
#     docker_url="unix://var/run/docker.sock",
#     network_mode="bridge",
#     dag=dag,
# )
#
# validate_chart_task >> train_task
