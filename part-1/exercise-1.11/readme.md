# Requirements

Let's share data between "Ping-pong" and "Log output" applications using persistent volumes. Create both a PersistentVolume and PersistentVolumeClaim and alter the Deployment to utilize it. As PersistentVolumes are often maintained by cluster administrators rather than developers and those are not application specific you should keep the definition for those separated, perhaps in own folder.

Save the number of requests to "Ping-pong" application into a file in the volume and output it with the timestamp and hash when sending a request to our "Log output" application. In the end, the two pods should share a persistent volume between the two applications. So the browser should display the following when accessing the "Log output" application:

```
2020-03-30T12:15:17.705Z: 8523ecb1-c716-4cb6-a044-b9e83bb98e43.
Ping / Pongs: 3
```

# Solution

## Create persistent volume

I first create a local path in the local node to bind the persistent volume into.

- `docker exec k3d-k3s-default-agent-0 mkdir -p /tmp/kube`

Then I write `persistentvolume.yaml`:

```
apiVersion: v1
kind: PersistentVolume
metadata:
  name: example-pv
spec:
  storageClassName: my-example-pv 
  capacity:
    storage: 1Gi 
  volumeMode: Filesystem
  accessModes:
  - ReadWriteOnce
  local:
    path: /tmp/kube
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - k3d-k3s-default-agent-0
```

Finally I write the claims for this volume.

```
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: image-claim 
spec:
  storageClassName: my-example-pv 
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

Now I modify `log-output-deployment.yaml` so that is utilizes this persistent volume instead of an `emptyDir`.

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dwk-log-output
spec:
  ...
  template:
    ...
    spec:
      volumes:
        - name: shared-image
          persistentVolumeClaim:
            claimName: image-claim
```

We need to share files between pods, so I modify `ping-pong-deployment.yaml` as well, so that it utilizes the persistent volume.

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dwk-ping-pong
spec:
  ...
  template:
    ...
    spec:
      volumes:
        - name: shared-image
          persistentVolumeClaim:
            claimName: image-claim
      containers:
        - name: dwk-ping-pong
          ...
          volumeMounts:
          - name: shared-image
            mountPath: /usr/src/app/files
```

Now we should be sharing a persistent volume between pods `log-output` and `ping-pong`.

## Modify application `ping-pong`

I modify my `ping-pong.py` application so that it can save an integer to a file in the shared persistent volume.

```
def save_pings_to_persistent_volume(pings:int):
    # save n_requests to persistent volume
    fname = 'ping-pong.txt'
    fdir = os.path.join('/', 'usr', 'src', 'app', 'files')
    fpath = os.path.join(fdir, fname)

    # create file if not exist
    if fname not in os.listdir(fdir):
        with open(fpath, 'w'):
            pass

    # write to file
    with open(fpath, "w") as f:
        f.write(f"{pings}")
```

This function is called when the server first launches, innitializing accumulated pings to `0`. Then, it is called again each time a request is made to endpoint `/pingpong`.

## Modify application `log-output`

Both `reader` and `writer` of application `Log-output` should read value of `pings` from the persistent volume every time a request is received. I write a function for that:

```
def get_pings():
    # load pings from persistent volume
    fname = 'ping-pong.txt'
    fdir = os.path.join('/', 'usr', 'src', 'app', 'files')
    fpath = os.path.join(fdir, fname)

    # return 0 if not exist
    if fname not in os.listdir(fdir):
        return 0

    # read pings from file
    with open(fpath, 'r') as f:
        return int(f.read())
```

Then the above function is called every time a request is made to endpoints `/now/reader` and `/now/writer`.

```
# dummy endpoint 
@app.get("/now/reader", response_class=PlainTextResponse)
def read_root():
    return f"{get_current_timestamp()}.\nPing / Pongs : {get_pings()}"
```

## Deployment and validation

Build the images and import to the cluster:

- `docker build -f log-output-writer.Dockerfile . --tag dwk-log-output-writer:1.11.0`
- `docker build -f log-output-reader.Dockerfile . --tag dwk-log-output-reader:1.11.0`
- `docker build -f ping-pong.Dockerfile . --tag dwk-ping-pong:1.11.0`
- `k3d image import dwk-log-output-writer:1.11.0 dwk-log-output-reader:1.11.0 dwk-ping-pong:1.11.0`

Deploy to the cluster:

- `kubectl apply -f manifests/`

  ```
  ingress.networking.k8s.io/dwk-log-output-ing created
  deployment.apps/dwk-log-output created
  service/dwk-log-output-svc created
  persistentvolume/example-pv created
  persistentvolumeclaim/image-claim created
  deployment.apps/dwk-ping-pong created
  service/dwk-ping-pong-svc created
  ```

Let's see if everything works as intended.

- `curl 127.0.0.1:8081/now/reader`

  ```
  2025-01-28T23:03:45.883Z: 0234fd9c-c5b5-4c89-994d-a77c7c22f0d5.
  Ping / Pongs : 0
  ```

- `curl 127.0.0.1:8081/pingpong`

  ```
  "Pong 1"
  ```

- `curl 127.0.0.1:8081/pingpong`

  ```
  "Pong 1"
  ```

- `curl 127.0.0.1:8081/pingpong`

  ```
  "Pong 1"
  ```

- `curl 127.0.0.1:8081/now/reader`

  ```
  2025-01-28T23:04:17.912Z: 4dd05594-f2e5-4f0c-82af-a530fcfda312.
  Ping / Pongs : 3
  ```

Works as intended!