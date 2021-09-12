#!/bin/bash


# kubectl create namespace flowi
helm repo add dask https://helm.dask.org/
helm repo update
helm install dask dask/dask --set serviceType=NodePort -n flowi
helm upgrade --install dask dask/dask  --values values.yaml  -n flowi


#Thank you for installing DASK, released at name: dask.
#
#To learn more about the release, try:
#
#  $ helm status dask  # information about running pods and this message
#  $ helm get dask     # get full Kubernetes specification
#
#This release includes a Dask scheduler, 3 Dask workers, and 1 Jupyter servers.
#
#The Jupyter notebook server and Dask scheduler expose external services to
#which you can connect to manage notebooks, or connect directly to the Dask
#cluster. You can get these addresses by running the following:
#
#  export DASK_SCHEDULER="127.0.0.1"
#  export DASK_SCHEDULER_UI_IP="127.0.0.1"
#  export DASK_SCHEDULER_PORT=8080
#  export DASK_SCHEDULER_UI_PORT=8081
#  kubectl port-forward --namespace dask svc/dask-scheduler $DASK_SCHEDULER_PORT:8786 &
#  kubectl port-forward --namespace dask svc/dask-scheduler $DASK_SCHEDULER_UI_PORT:80 &
#
#  export JUPYTER_NOTEBOOK_IP="127.0.0.1"
#  export JUPYTER_NOTEBOOK_PORT=8082
#  kubectl port-forward --namespace dask svc/dask-jupyter $JUPYTER_NOTEBOOK_PORT:80 &
#
#  echo tcp://$DASK_SCHEDULER:$DASK_SCHEDULER_PORT               -- Dask Client connection
#  echo http://$DASK_SCHEDULER_UI_IP:$DASK_SCHEDULER_UI_PORT     -- Dask dashboard
#  echo http://$JUPYTER_NOTEBOOK_IP:$JUPYTER_NOTEBOOK_PORT       -- Jupyter notebook
#
#NOTE: It may take a few minutes for the LoadBalancer IP to be available. Until then, the commands above will not work for the LoadBalancer service type.
#You can watch the status by running 'kubectl get svc --namespace dask -w dask-scheduler'
#
#NOTE: It may take a few minutes for the URLs above to be available if any EXTRA_PIP_PACKAGES or EXTRA_CONDA_PACKAGES were specified,
#because they are installed before their respective services start.
#
#NOTE: The default password to login to the notebook server is `dask`. To change this password, refer to the Jupyter password section in values.yaml, or in the README.md.
