# Requirements
In your "Log output" application create a folder for manifests and move your deployment into a declarative file.

Make sure everything still works by restarting and following logs.

# Solution

## Create manifests/deployment.yaml

I decide to rename my image from exercise 1.01. From now on I use the image name `dwk-log-output`. 

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
          image: dwk-log-output:latest
          imagePullPolicy: Never
```
I also added `imagePullPolicy: Never` - Now I don't have to run `kubectl edit deployment` each time I apply a deployment.

## Build Image and import to k3d
The dockerfile remains the same as that of exercise 1.01. However since I decided to rename the image I build and import it again:

- `docker build -f Dockerfile . --tag dwk-log-output:latest`
- `k3d image import dwk-log-output:latest`

## Apply deployment.yaml to the cluster

- `kubectl apply -f manifests/deployment.yaml`

## Analyze logs

Theoretically, that should do it. Let's see if everything is up and running:

- `kubectl get deployments`

    ```
    dwk-log-output      1/1     1            1           16s
    hashgenerator-dep   1/1     1            1           3h25m
    project-dep         1/1     1            1           67m
    ```

- `kubectl logs deployments/dwk-log-output`
    ```
    2025-01-28T00:30:17.203Z: 77eb835d-ae49-42d7-8d2e-03f1de7e8ba0
    2025-01-28T00:30:22.204Z: 9e08b6d9-bda7-4f4d-9fbd-cd97e5d9b300
    2025-01-28T00:30:27.205Z: 19d79855-27bc-435f-9f5b-1595e48ddde0
    2025-01-28T00:30:32.206Z: ed405eac-ac00-437c-a11f-08a63d4062f3
    2025-01-28T00:30:37.207Z: ab87875f-6469-4553-ac77-5437dbf3f1de
    2025-01-28T00:30:42.208Z: 8a38572f-efd2-4746-a123-5612a84719d8
    2025-01-28T00:30:47.209Z: df9cf365-2ebd-4555-b52b-243e86ea9b35
    2025-01-28T00:30:52.211Z: 8174ef07-8520-46bb-908d-29e85f652b6d
    2025-01-28T00:30:57.212Z: d0b54a3c-2f58-4733-8fb8-232fad5c0caf
    ...
    ```

Nicely done!