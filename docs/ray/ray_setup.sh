kubectl create namespace ray

kubectl -n ray apply -f ray_cluster_crd.yml
kubectl -n ray apply -f ray_operator.yml
kubectl -n ray apply -f ray_cluster.yml
