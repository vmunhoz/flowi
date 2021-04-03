kubectl delete pods --namespace default --field-selector=status.phase=Succeeded -l spark-role=driver
