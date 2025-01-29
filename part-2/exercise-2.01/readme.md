# Requirements

Connect the "Log output" application and "Ping-pong" application. Instead of sharing data via files use HTTP endpoints to respond with the number of pongs. Deprecate all the volume between the two applications for the time being.

The output will stay the same:

```
2020-03-30T12:15:17.705Z: 8523ecb1-c716-4cb6-a044-b9e83bb98e43.
Ping / Pongs: 3
```

# Solution

## Deprecate persistent volume

The requirements specify that we remove any shared volume between the two deployments `log-output` and `ping-pong`. The volume is still needed for the `log-output-reader` and `log-output-writer` to communicate, so I will keep it. However I will revoke volume access from `ping-pong`.

- `ping-pong-deployment.yaml` - removed `volume` related blocks.

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
            image: dwk-ping-pong:1.11.0
            imagePullPolicy: Never
            env:
              - name: PORT
                value: "7777"
  ```

## Edit `/pingpong` endpoint 

Now that the `persistentvolume` is gone, we need to store the number of `pings` in memory again.

```
import uvicorn, os
from fastapi import FastAPI

app = FastAPI()
host = "0.0.0.0"  
port = int(os.environ["PORT"])

app.state.n_requests = 0

@app.get("/pingpong")
def read_root():
    app.state.n_requests += 1
    return f"Pong {app.state.n_requests}"

if __name__ == "__main__":
    uvicorn.run(app, host=host, port=port)
```

The application is back to being simple and thin again. I also add a new endpoint to return the current number of pings without incrementing it.

```
...
@app.get("/get_pings", response_class=PlainTextResponse)
def get_pings():
    return f"{app.state.n_requests}"
...
```

## Edit `get_pings` logic

We now need to modify the `get_pings` function of the `log-output` applications, in both `reader` and `writer`. Instead of fetching the number of pings from a file, we want them to call an endpont instead. With [official documentation](https://kubernetes.io/docs/tutorials/services/connect-applications-service/#environment-variables) as reference, I decide to use pod-level environment variables to acess services from applications.

```
ping_pong_service_host:str = os.environ["DWK_PING_PONG_SVC_SERVICE_HOST"]
ping_pong_service_port:int = int(os.environ["DWK_PING_PONG_SVC_SERVICE_PORT"])

def get_pings() -> str:
    # fetch pings from endpoint
    pings = requests.get(f'http://{ping_pong_service_host}:{ping_pong_service_port}/pingpong')
    return pings.text
```

## Build and deploy

I write a simple `makefile` again to use for deployment.

```
deploy:
	@docker build -f log-output-reader.Dockerfile . --tag dwk-log-output-reader:2.1.0
	@docker build -f log-output-writer.Dockerfile . --tag dwk-log-output-writer:2.1.0
	@docker build -f ping-pong.Dockerfile . --tag dwk-ping-pong:2.1.0 && echo "\n"
	@k3d image import dwk-log-output-reader:2.1.0 dwk-log-output-writer:2.1.0 dwk-ping-pong:2.1.0 && echo "\n"
	@kubectl delete -f manifests/ && echo "\n"
	@kubectl apply -f manifests/ && echo "\n"
	@sleep 5
	@kubectl get deployments && echo "\n"
	@kubectl get services && echo "\n"
	@kubectl get pods
```

Now I call `make deploy` to launch the service into the cluster:

```
...
ingress.networking.k8s.io/dwk-log-output-ing created
deployment.apps/dwk-log-output created
service/dwk-log-output-svc created
persistentvolume/example-pv created
persistentvolumeclaim/image-claim created
deployment.apps/dwk-ping-pong created
service/dwk-ping-pong-svc created

NAME             READY   UP-TO-DATE   AVAILABLE   AGE
dwk-log-output   1/1     1            1           5s
dwk-ping-pong    1/1     1            1           5s

NAME                 TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
dwk-log-output-svc   ClusterIP   10.43.190.255   <none>        7777/TCP,7778/TCP   5s
dwk-ping-pong-svc    ClusterIP   10.43.100.192   <none>        2345/TCP            5s
kubernetes           ClusterIP   10.43.0.1       <none>        443/TCP             13h

NAME                             READY   STATUS    RESTARTS   AGE
dwk-log-output-f875c5c9c-q4fkk   2/2     Running   0          5s
dwk-ping-pong-6ff7d4d7b6-98scn   1/1     Running   0          5s
```

## Test the outputs

- `curl 127.0.0.1:8081/now/reader`

  ```
  2025-01-29T15:25:45.727Z: 5e4bb3ad-e078-44a1-bd9b-21cbb354c8ac.
  Ping / Pongs : 0
  ```
- `curl 127.0.0.1:8081/pingpong`

  ```
  Pong 1   
  ```
- `curl 127.0.0.1:8081/pingpong`

  ```
  Pong 2   
  ```
- `curl 127.0.0.1:8081/pingpong`

  ```
  Pong 3   
  ```
- `curl 127.0.0.1:8081/now/reader`

  ```
  2025-01-29T15:25:57.660Z: 8a2bbbe0-f5ce-478c-bd99-643fbda8c713.
  Ping / Pongs : 3                               
  ```

Our applications `ping-pong` and `log-output` are now communicating without a shared `persistentvolume`.
