# Requirements

Create a web server that outputs "Server started in port NNNN" when it is started and deploy it into your Kubernetes cluster. Please make it so that an environment variable PORT can be used to choose that port. You will not have access to the port when it is running in Kubernetes yet. We will configure the access when we get to networking.

# Solution

## Create application

I create my server application with `FastAPI` and serve it with `uvicorn`. I choose to invoke `python main.py` in the command line to run uvicorn in `main.py`. This allows me to specify the port I want the server to run on in `main.py`. I script my code so that it imports the value set in the environment variable `PORT`.

```
import uvicorn, os
from fastapi import FastAPI

app = FastAPI()
host = "0.0.0.0"

# dynamic port allocation here
port = int(os.environ["PORT"])

# dummy endpoint 
@app.get("/health-check")
def read_root():
    return {"message": "OK"}

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)
```

Again, implementation details are available in the comments of `main.py`.

## Dockerizing my server application

Again I dockerize my application. 

```
FROM python:3.11.11-alpine3.21
WORKDIR /usr/src/app

# install python web server packages
RUN pip install fastapi uvicorn

COPY src src
ENV PYTHONUNBUFFERED=1

# environment variable PORT can be used to choose the port the server runs on
ENV PORT=7777
EXPOSE ${PORT}

# start server
CMD ["python", "src/main.py"]
```

Let's give it a test run:

- `docker build -f Dockerfile . --tag dwk-project`
- `docker run -dit --name dwk-project -p 7777:7777 dwk-project`

FastAPI automatically outputs some strings on startup, including `Uvicorn running on <host>:<port>`. Let's check the logs.
- `docker logs dwk-project`

    ```
    INFO:     Started server process [1]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://0.0.0.0:7777 (Press CTRL+C to quit)
    INFO:     172.17.0.1:55220 - "GET /health-check HTTP/1.1" 200 OK
    ```

The server is running nicely on the specified port. Now a `curl` to the dummy endpoint should return the message `OK`.

- `curl 127.0.0.1:7777/health-check`

    ```
    {"message":"OK"}
    ```

# Deploy to Kubernetes

Again, we are deploying a local image to Kubernetes. Therefore we will create a new deployment in the existing cluster, then use `kubectl edit` to update the `ImagePullPolicy` to `Never`. I also import the built image into the cluster first.

- `k3d image import dwk-project:latest`

- `kubectl create deployment project-dep --image=dwk-project`

- `kubectl get deployments`

    ```
    NAME                READY   UP-TO-DATE   AVAILABLE   AGE
    hashgenerator-dep   1/1     1            1           138m
    project-dep         0/1     1            0           18s
    ```
Again, we see `READY 0/1`. This is perfectly normal. Let's update the `ImagePullPolicy` to `Never`.

- `kubectl edit deployment`

    ```
    spec:
    ...
    template:
        ...
        spec:
        ...
        containers:
        - image: dwk-project
            imagePullPolicy: Never
            ...
    ```
    output is as follows:
    ```
    deployment.apps/hashgenerator-dep skipped
    deployment.apps/project-dep edited
    ```

Let's see if the server is up and running now:
- `kubectl get deployments`

    ```
    hashgenerator-dep   1/1     1            1           145m
    project-dep         1/1     1            1           6m57s
    ```
- `kubectl logs deployments/project-dep dwk-project` 

    ```
    INFO:     Started server process [1]
    INFO:     Waiting for application startup.
    INFO:     Application startup complete.
    INFO:     Uvicorn running on http://0.0.0.0:7777 (Press CTRL+C to quit)
    ```

The server is now running in the cluster.