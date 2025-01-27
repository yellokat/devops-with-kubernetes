# Requirements
Exercises can be done with any language and framework you want.

Create an application that generates a random string on startup, stores this string into memory, and outputs it every 5 seconds with a timestamp. e.g.

```
2020-03-30T12:15:17.705Z: 8523ecb1-c716-4cb6-a044-b9e83bb98e43
2020-03-30T12:15:22.705Z: 8523ecb1-c716-4cb6-a044-b9e83bb98e43
```

Deploy it into your Kubernetes cluster and confirm that it's running with kubectl logs ...

You will keep building this application in the future exercises. This application will be called "Log output".

# Solution

## Create application

I write a simple python application:

```
import time, uuid, re
from datetime import datetime, timezone

if __name__ == "__main__":
    while(True):
        current_timestamp = re.sub('\+00:00', 'Z', datetime.now(timezone.utc).isoformat(timespec="milliseconds"))
        random_string = str(uuid.uuid4())
        print(f"{current_timestamp}: {random_string}")
        time.sleep(5)
```
Detailed explanations for implementation is in the comments of `main.py`. To briefly explain:

- Use UTC, use "Z" instead of "+00:00"
- Express current timestamp up to milliseconds
- Use UUID4 for random string generation
- Repeat indefinitely every 5 seconds using `while(True)` and `time.sleep(5)`.

## Build Image
I dockerize this application in a lightweight python based container. 
```
FROM python:3.11.11-alpine3.21

WORKDIR /usr/src/app
COPY src src
ENV PYTHONUNBUFFERED=1

CMD ["python", "src/main.py"]
```
Again, the implementation details are in the comments of the `Dockerfile`. To summarize:
- Use `alpine`.
- I use `python 3.11.2` locally, so for convenience I choose a container based on python `3.11.11`.
- Disable python's buffered print behavior so that kubernetes understands it.

Now I build this image locally and tag it `dwk-ex1.01:latest`. Then I run a test launch to see if the application logic is correct:
- `docker build -f Dockerfile . --tag dwk-ex1.01:latest`
- `docker run -dit --name dwk dwk-ex1.01:latest`
- `docker logs dwk -f`

This gives the following output.
```
2025-01-27T20:17:19.623Z: 433166d4-d367-4459-bfa4-d5bba50d8628
2025-01-27T20:17:24.625Z: ca659a92-b810-4bc1-8a09-20d8d869c1db
2025-01-27T20:17:29.626Z: d1d669e8-10c2-43c4-a347-4e5770adc50d
2025-01-27T20:17:34.627Z: 103c2745-f19a-4e6d-886e-f5e5a8032e09
...
```
Seems like everything is working well. I kill the container and remove it using:
- `docker kill dwk`
- `docker remove dwk`

## Launch the cluster and import local image
I set up the k3d cluster with:
- `k3d cluster create -a 2`

I check that all is up and running:
- `kubectl cluster-info`

    ```
    Kubernetes control plane is running at https://0.0.0.0:51629
    CoreDNS is running at https://0.0.0.0:51629/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
    Metrics-server is running at https://0.0.0.0:51629/api/v1/namespaces/kube-system/services/https:metrics-server:https/proxy
    ```
Following the course material I run the following commands to import the local image into k3d:
- `k3d image import dwk-ex1.01:latest`

    ```
    INFO[0000] Importing image(s) into cluster 'k3s-default' 
    INFO[0000] Starting new tools node...                   
    INFO[0000] Starting node 'k3d-k3s-default-tools'        
    INFO[0000] Saving 1 image(s) from runtime...            
    INFO[0001] Importing images into nodes...               
    INFO[0001] Importing images from tarball '/k3d/images/k3d-k3s-default-images-20250128042103.tar' into node 'k3d-k3s-default-agent-1'... 
    INFO[0001] Importing images from tarball '/k3d/images/k3d-k3s-default-images-20250128042103.tar' into node 'k3d-k3s-default-agent-0'... 
    INFO[0001] Importing images from tarball '/k3d/images/k3d-k3s-default-images-20250128042103.tar' into node 'k3d-k3s-default-server-0'... 
    INFO[0003] Removing the tarball(s) from image volume... 
    INFO[0004] Removing k3d-tools node...                   
    INFO[0005] Successfully imported image(s)               
    INFO[0005] Successfully imported 1 image(s) into 1 cluster(s) 
    ```
## Create a deployment and edit configurations

Following the course I run the following to create a deployment:
- `kubectl create deployment hashgenerator-dep --image=dwk-ex1.01:latest`

Unfortunately this doesn't work yet because I haven't configured k3d to use local images.
- `kubectl get deployments`

    ```
    NAME                READY   UP-TO-DATE   AVAILABLE   AGE
    hashgenerator-dep   0/1     1            0           6s
    ```

As expected, I see `READY 0/1`. Now I edit the imagePullPolicy with:
- `kubectl edit deployment hashgenerator-dep`

    ```
    spec:
    ...
    template:
        ...
        spec:
        ...
        containers:
        - image: dwk-ex1.01
            imagePullPolicy: Never
            ...
    ```
An output message tells me that deployment config has been updated.

```
deployment.apps/hashgenerator-dep edited
```

Now I can check if everything works:
- `kubectl get deployments`

    ```
    NAME                READY   UP-TO-DATE   AVAILABLE   AGE
    hashgenerator-dep   1/1     1            1           4m25s
    ```

The deployment is up and running. I analyze the logs:

- `kubectl logs hashgenerator-dep-8695fdd67d-m6lk5`

    ```
    2025-01-27T21:09:09.701Z: 461ecfcd-38ff-47d4-82a0-bdfb7e9289fa
    2025-01-27T21:09:14.702Z: 73e172e8-8506-4be9-a941-90239d8d629c
    2025-01-27T21:09:19.703Z: 104aad46-f145-4fee-9db7-647a500cdea2
    2025-01-27T21:09:24.704Z: 42f92a9d-8308-4f3a-a302-7f4a215b7157
    2025-01-27T21:09:29.705Z: 71149c4f-9b22-452a-a6ea-faa1070f7553
    2025-01-27T21:09:34.706Z: 4571ad06-8a24-4209-a5d5-07756b40d464
    2025-01-27T21:09:39.707Z: 9534935d-f10a-4070-bd92-a60ab4dd5728
    2025-01-27T21:09:44.708Z: c149797a-32de-4704-88f0-da4722dc942b
    ...
    ```
