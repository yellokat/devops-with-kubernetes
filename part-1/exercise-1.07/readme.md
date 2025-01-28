# Requirements

"Log output" application currently outputs a timestamp and a random string to the logs.

Add an endpoint to request the current status (timestamp and string) and an ingress so that you can access it with a browser.

You can just store the string and timestamp to the memory.

# Solution

## Update source application

I add a lightweight server application to the `log_output` app so that it now holds a simple endpoint to return the current timestamp string. I extract the existing logic to generate timestamp strings and reuse it in my endpoint.

Additionally, we now need to run two never-ending processes in parallel. I make use of python's `threading` library to achieve this.
```
import time, uuid, re, uvicorn, os
from fastapi import FastAPI
from datetime import datetime, timezone
from threading import Thread

# initialize FastAPI app
app = FastAPI()

# enable local network
host = "0.0.0.0"  

# inherit from environment variable
port = int(os.environ["PORT"])

# extract the function to generate the timestamp
def get_current_timestamp():
    ...
    return f"{current_timestamp}: {random_string}"

# endpoint to return current timestamp string, as requirements specify
@app.get("/now")
def read_root():
    return {"message": get_current_timestamp()}

# thread job - infinitely log output every 5 seconds
def log_output():
    while(True):
        # print current timestampt every 5 seconds
        print(get_current_timestamp())
        time.sleep(5)

# thread job - run the server
def run_server(host, port):
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    # initialize two threads, one for logging output and one for running the server
    thread1 = Thread(target=log_output)
    thread2 = Thread(target=run_server, args=(host, port))

    # Start both threads
    thread1.start()
    thread2.start()
```

The dockerfile has to be edited as well, since new package dependencies have been added. We omit declaration of environment variable `PORT` and exposing that port, since this will all be taken care of by kubernetes.

```
FROM python:3.11.11-alpine3.21
WORKDIR /usr/src/app

RUN pip install fastapi uvicorn
COPY src src

ENV PYTHONUNBUFFERED=1
CMD ["python", "src/main.py"]
```

I build my image and import it into k3d.

- `docker build . --tag dwk-log-output:1.7.0`
- `k3d image import dwk-log-output:1.7.0`

## Update deployment

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dwk-log-output
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dwk-log-output
  template:
    metadata:
      labels:
        app: dwk-log-output
    spec:
      containers:
        - name: dwk-log-output
          image: dwk-log-output:1.7.0
          imagePullPolicy: Never
          env:
            - name: PORT
              value: "7777"
```

I use the previously created `deployment.yaml` from `exercise 1.03`, but I bumped the image tag to `1.7.0`, for `exercise 1.07`. I also specify the port (`7777`) to use for the web server application.

## Create manifests/ingress.yaml

This ingress will forward all requests at port `2345` to service `dwk-log-output-svc`.

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
```

## Create service.yaml
I create a `service.yaml` that declares a `ClusterIP` service. It should redirect all requests to port `2345` to port `7777` of the container running inside our pod.

```
apiVersion: v1
kind: Service
metadata:
  name: dwk-log-output-svc
spec:
  type: ClusterIP
  selector:
    app: dwk-log-output
  ports:
    - port: 2345 
      protocol: TCP
      targetPort: 7777 # This is the target port
```

## Apply and validate

- `kubectl apply -f manifests`

  ```
  deployment.apps/dwk-log-output created
  ingress.networking.k8s.io/dwk-log-output-ing created
  service/dwk-log-output-svc created
  ```

- `kubectl get svc,ing`

  ```
  NAME                      TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
  ingress.networking.k8s.io/dwk-log-output-ing     traefik   *       172.18.0.2,172.18.0.4,172.18.0.5   80      28s
  ingress.networking.k8s.io/dwk-material-ingress   traefik   *       172.18.0.2,172.18.0.4,172.18.0.5   80      56m
  ```

Let's see if our setup works as intended.
- `kubectl logs deployments/dwk-log-output`

  ```
  2025-01-28T17:02:51.823Z: 5c52db80-a69f-4b3c-b879-d1b3081718e0
  INFO:     Started server process [1]
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://0.0.0.0:7777 (Press CTRL+C to quit)
  2025-01-28T17:02:56.825Z: 8f86354c-0656-42bd-ae30-b0aa88472655
  2025-01-28T17:03:01.826Z: 80adca52-2e13-4a17-9661-584cfb622ff3
  2025-01-28T17:03:06.828Z: 447c040b-63fa-4f05-a77e-c02b06222926
  2025-01-28T17:03:11.829Z: 9075a496-8f95-4503-a8fc-0f61748f13c1
  2025-01-28T17:03:16.830Z: 1c7d821b-1d7f-4ca9-a00e-671f50cbed96
  ...
  ```

  We see the server and the log output application both running in parallel.

- `curl 127.0.0.1:8081/now`

  ```
  {"message":"2025-01-28T17:03:52.448Z: f6206682-38bf-4b88-9e4d-e1cb4c851d4a"}
  ```

  The endpoint that returns the current timestamp is also working well.
