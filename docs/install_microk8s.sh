sudo snap install microk8s --classic --channel=1.21/stable
sudo usermod -a -G microk8s $USER
sudo chown -f -R $USER ~/.kube
#su - $USER
sudo microk8s status --wait-ready
newgrp microk8s

# Setup microk8s
microk8s enable istio helm3 registry
sudo snap alias microk8s.kubectl kubectl
sudo snap alias microk8s.helm3 helm3
sudo snap alias microk8s.helm3 helm


echo "Contanier registry: $(kubectl get service/registry -o jsonpath='{.spec.clusterIP}' -n container-registry)"
