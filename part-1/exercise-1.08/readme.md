# Requirements

Switch to using Ingress instead of NodePort to access the project. You can delete the ingress of the "Log output" application so they don't interfere with this exercise. We'll look more into paths and routing in the next exercise and at that point you can configure project to run with the "Log output" application side by side.

# Solution

## Create manifests/ingress.yaml

This ingress will forward all requests at port `2345` to service `dwk-project-svc`.

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dwk-material-ingress
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dwk-project-svc
            port:
              number: 2345
```

## Edit service.yaml
I edit `service.yaml` so that it declares a `ClusterIP` service instead of a `NodePort` service. It should redirect all requests to port `2345` to port `7777` of the container running inside our pod.

```
apiVersion: v1
kind: Service
metadata:
  name: dwk-project-svc
spec:
  type: ClusterIP
  selector:
    app: dwk-project
  ports:
    - port: 2345 
      protocol: TCP
      targetPort: 7777 # This is the target port
```

## Apply and validate

- `kubectl get svc,ing`

  ```
  NAME                      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
  service/dwk-project-svc   ClusterIP   10.43.255.85   <none>        2345/TCP   6m17s
  service/kubernetes        ClusterIP   10.43.0.1      <none>        443/TCP    116m
  ```

Let's see if our setup works as intended.
- `curl 127.0.0.1:8081/health-check`

  ```
  {"message":"OK"}
  ```

