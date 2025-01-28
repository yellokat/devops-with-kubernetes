# Requirements

Create a deployment.yaml for the project.

You won't have access to the port yet but that'll come soon.

# Solution

## Creating manifests/deployment.yaml

Things are pretty much the same from exericse 1.03.

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
          image: dwk-project:latest
          imagePullPolicy: Never
```

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