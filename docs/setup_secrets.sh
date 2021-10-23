#!/bin/bash

cat <<EOF | kubectl apply -f -
apiVersion: v1
data:
  minio-admin-access-key: $(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12 | base64)
  minio-admin-secret-key: $(head /dev/urandom | tr -dc A-Za-z0-9 | head -c 12 | base64)
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

kubectl get secret flowi-secrets -o go-template='{{range $k,$v := .data}}{{"### "}}{{$k}}{{"\n"}}{{$v|base64decode}}{{"\n\n"}}{{end}}'
