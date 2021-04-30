#/bin/bash

cat <<EOF | kubectl apply -f -
apiVersion: v1
data:
  minio-access-key: $(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12 | base64)
  minio-secret-key: $(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12 | base64)
  mysql-user: $(printf "flowi_user"| base64)
  mysql-password: $(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12 | base64)
  mysql-root-password: $(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12 | base64)
kind: Secret
type: Opaque
metadata:
  name: flowi-secrets
  namespace: flowi
EOF

kubectl describe secrets/flowi-secrets
