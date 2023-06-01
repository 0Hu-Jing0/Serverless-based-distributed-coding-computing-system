while true
do
    kubectl top nodes -n openfaas-fn
    sleep 1
done