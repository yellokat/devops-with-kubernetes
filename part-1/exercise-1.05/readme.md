# Requirements

Have the project respond something to a GET request sent to the project. A simple html page is good or you can deploy something more complex like a single-page-application.

See here how you can define environment variables for containers.

Use kubectl port-forward to confirm that the project is accessible and works in the cluster by using a browser to access the project.

# Solution

## Modifying docker image 

Previously I had assigned the environment variable `PORT` in the dockerfile and had the python server app pick it up from the environment variable. Now that I want kubernetes (`deployment.yaml`)  to handle assignment of `PORT` environment variable, I remove it from the dockerfile.

```
FROM python:3.11.11-alpine3.21
WORKDIR /usr/src/app
RUN pip install fastapi uvicorn
COPY src src
ENV PYTHONUNBUFFERED=1

# environment variable PORT can be used to choose the port the server runs on
# ENV PORT=7777
# EXPOSE ${PORT}

CMD ["python", "src/main.py"]
```

Then I rebuild the image, and import it to k3d. 
- `docker build . --tag dwk-project:1.5.0`
- `k3d image import dwk-project:1.5.0`

Also from now on, I decide to manage my image versions as `<part_number>.<exercise_number>.<patch>`.

## Modifying deployment.yaml

I add the environment variable `PORT` to `deployment.yaml` and assign port 7777. Since I stopped using `latest` for every version and introduced version numbers to my image, I also change the image version string accordingly.

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dwk-project
spec:
  replicas: 1
  selector:
    matchLabels:
      app: dwk-project
  template:
    metadata:
      labels:
        app: dwk-project
    spec:
      containers:
        - name: dwk-project
          image: dwk-project:1.5.0
          imagePullPolicy: Never
          env:
            - name: PORT
              value: "7777"
```

Now I run `kubectl apply -f manifests/deployment.yaml`.
I already have a dummy endpoint `health-check` set up in the server application. 

## Apply deployment.yaml and observe logs

- `kubectl apply -f manifests/deployment.yaml`

- `kubectl logs deployments/dwk-project`

    ```
    INFO:     Started server process [1]
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://0.0.0.0:7777 (Press CTRL+C to quit)
    ```

We see that our server is up and running.

## Port forwarding

I forward our local port `7777` to the pod's port `7777`. 

- `kubectl port-forward dwk-project-7fdcb9cd9c-vb2nq 7777:7777`

  ```
  Forwarding from 127.0.0.1:7777 -> 7777
  Forwarding from [::1]:7777 -> 7777
  ```

The port forwarding command runs in the foreground until I hit `Ctrl+c` to stop port forwarding. As long as the port forwarding process is running, I can access the local port `7777` to check out my application deployed in kubernetes.

Let's test the connection locally.

- `curl http://127.0.0.1:7777/health-check`

  ```
  {"message":"OK"}
  ```

Thus it is verified that our dummy endpoint (`health-check`) is properly running.