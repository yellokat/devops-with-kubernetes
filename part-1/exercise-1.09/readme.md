# Requirements

Develop a second application that simply responds with "pong 0" to a GET request and increases a counter (the 0) so that you can see how many requests have been sent. The counter should be in memory so it may reset at some point. Create a new deployment for it and have it share ingress with "Log output" application. Route requests directed '/pingpong' to it.

In future exercises, this second application will be referred to as "ping-pong application". It will be used with "Log output" application.

The ping-pong application will need to listen requests on '/pingpong', so you may have to make changes to its code. This can be avoided by configuring the ingress to rewrite the path, but we will leave that as an optional exercise. You can check out https://kubernetes.io/docs/concepts/services-networking/ingress/#the-ingress-resource

# Solution

## Edit existing application

I will add a new python source file and Dockerfile for the `ping-pong` application. Before I do that, I adjust some names to make it less general and more task-specific.
- `main.py` -> `log-output.py`

- `Dockerfile` -> `log-output.Dockerfile`

  ```
  FROM python:3.11.11-alpine3.21

  ...

  # run log-output.py instead of main.py
  CMD ["python", "src/log-output.py"]
  ```

## Add new application

I write a new application `ping-pong.py`, again using `FastAPI` and `Uvicorn`.

```
import time, uuid, re, uvicorn, os
from fastapi import FastAPI
from datetime import datetime, timezone
from threading import Thread

app = FastAPI()
host = "0.0.0.0"  
port = int(os.environ["PORT"])

# keep track of how many requests were made
app.state.n_requests = 0

# pingpong endpoint 
@app.get("/pingpong")
def read_root():
    # increment locally stored value
    app.state.n_requests += 1
    return {"message": f"Pong {app.state.n_requests}"}

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)
```

I also create the Dockerfile for this application.

```
FROM python:3.11.11-alpine3.21
WORKDIR /usr/src/app

RUN pip install fastapi uvicorn
COPY src src

ENV PYTHONUNBUFFERED=1
CMD ["python", "src/ping-pong.py"]
```

Finally I build the images as `dwk-ping-pong:1.9.0` and `dwk-log-output:1.9.0` and import them into `k3d`.
- `docker build -f log-output.Dockerfile . --tag dwk-log-output:1.9.0`
- `docker build -f ping-pong.Dockerfile . --tag dwk-ping-pong:1.9.0`
- `k3d image import dwk-log-output:1.9.0 dwk-ping-pong:1.9.0`

  ```
  INFO[0000] Importing image(s) into cluster 'k3s-default' 
  INFO[0000] Starting new tools node...                   
  INFO[0000] Starting node 'k3d-k3s-default-tools'        
  INFO[0000] Saving 2 image(s) from runtime...            
  INFO[0002] Importing images into nodes...               
  INFO[0002] Importing images from tarball '/k3d/images/k3d-k3s-default-images-20250129013744.tar' into node 'k3d-k3s-default-server-0'... 
  INFO[0002] Importing images from tarball '/k3d/images/k3d-k3s-default-images-20250129013744.tar' into node 'k3d-k3s-default-agent-0'... 
  INFO[0002] Importing images from tarball '/k3d/images/k3d-k3s-default-images-20250129013744.tar' into node 'k3d-k3s-default-agent-1'... 
  INFO[0003] Removing the tarball(s) from image volume... 
  INFO[0004] Removing k3d-tools node...                   
  INFO[0004] Successfully imported image(s)               
  INFO[0004] Successfully imported 2 image(s) into 1 cluster(s) 
  ```

## Create new deployment and service

I create a separate `ping-pong-deployment.yaml` for the new application.

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dwk-ping-pong
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dwk-ping-pong
  template:
    metadata:
      labels:
        app: dwk-ping-pong
    spec:
      containers:
        - name: dwk-ping-pong
          image: dwk-ping-pong:1.9.0
          imagePullPolicy: Never
          env:
            - name: PORT
              value: "7777"
```
I also create a `ping-pong-service.yaml` that listens to requests and forwards it to the container `dwk-ping-pong`.
```
apiVersion: v1
kind: Service
metadata:
  name: dwk-ping-pong-svc
spec:
  type: ClusterIP
  selector:
    app: dwk-ping-pong
  ports:
    - port: 2345 
      protocol: TCP
      targetPort: 7777 # This is the target port
```
Additionally I rename the previous `yaml` files to avoid confusion:
- `deployment.yaml` -> `log-output-deployment.yaml`
- `service.yaml` -> `log-output-service.yaml`

## Edit `ingress.yaml`

The two deployments will share a single ingress. Requests made to this ingress will be redirected to applications `log-output` and `ping-pong` depending on path prefix.

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dwk-log-output-ing
spec:
  rules:
  - http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: dwk-log-output-svc
            port:
              number: 2345
      - path: /pingpong
        pathType: Prefix
        backend:
          service:
            name: dwk-ping-pong-svc
            port:
              number: 2345
```

## Deployment

- `kubectl apply -f manifests `

  ```
  ingress.networking.k8s.io/dwk-log-output-ing created
  deployment.apps/dwk-log-output unchanged
  service/dwk-log-output-svc created
  deployment.apps/dwk-ping-pong created
  service/dwk-ping-pong-svc created
  ```

- `kubectl get deployments`

  ```
  NAME             READY   UP-TO-DATE   AVAILABLE   AGE
  dwk-log-output   1/1     1            1           54m
  dwk-ping-pong    1/1     1            1           24s
  dwk-project      1/1     1            1           4h1m
  ```

Let's try calling our endpoints:

- `curl 127.0.0.1:8081/now`

  ```
  {"message":"2025-01-28T18:20:29.197Z: b319baf9-b1ed-4316-b38d-7cf7bd0fc50c"}
  ```
- `curl 127.0.0.1:8081/pingpong`

  ```
  {"message":"Pong 1"}
  ```
- `curl 127.0.0.1:8081/pingpong`

  ```
  {"message":"Pong 2"}
  ```
- `curl 127.0.0.1:8081/pingpong`

  ```
  {"message":"Pong 3"}
  ```
- `curl 127.0.0.1:8081/pingpong`

  ```
  {"message":"Pong 4"}
  ```
