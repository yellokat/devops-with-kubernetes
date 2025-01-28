# Requirements

Split the "Log output" application into two different containers within a single pod:

One generates a new timestamp every 5 seconds and saves it into a file.

The other reads that file and outputs it with a hash for the user to see.

Either application can generate the hash. The reader or the writer.

You may find this helpful now since there are more than one container running inside a pod.

# Solution

## Edit existing application

I split the existing `log-output.py` into two new files, and edit the function that prints timestamps every 5 seconds.

- `log-output-writer.py`

  ```
  def log_output_write():
    fname = 'timestamp.txt'
    fdir = os.path.join('/', 'usr', 'src', 'app', 'files')
    fpath = os.path.join(fdir, fname)

    # create file if not exist
    if fname not in os.listdir(fdir):
        with open(fpath, 'w'):
            pass

    # append current timestamp to file every 5 seconds
    while(True):
        with open(fpath, "a") as f:
            f.write(get_current_timestamp() + "\n")
        time.sleep(5)
  ```

  This function appends a timestamp string to `usr/src/app/files/timestamp.txt` every 5 seconds.

- `log-output-reader.py`

  ```
  def log_output_read():
    fname = 'timestamp.txt'
    fdir = os.path.join('/', 'usr', 'src', 'app', 'files')
    fpath = os.path.join(fdir, fname)

    # create file if not exist
    if fname not in os.listdir(fdir):
        with open(fpath, 'w'):
            pass

    last_read_line = 0
    while True:
        with open(fpath, 'r') as f:
            # read only newly appended lines, up to 100 new lines at a time
            for line in islice(f, last_read_line, last_read_line + 100):
                print(line.strip())
                last_read_line += 1
        time.sleep(0.5)
  ```

  This function opens `usr/src/app/files/timestamp.txt` and indefinitely polls for new lines every 0.5 seconds.

I also split the dockerfiles into two. Then I build the images and import them to `k3d`.

- `log-output-writer.py`

  ```
  # run main.py
  CMD ["python", "src/log-output-writer.py"]
  ```

- `log-output-reader.py`

  ```
  # run main.py
  CMD ["python", "src/log-output-reader.py"]
  ```

Then I build the images and load them into `k3d`.

- `docker build -f log-output-writer.Dockerfile . --tag dwk-log-output-writer:1.10.0`
- `docker build -f log-output-reader.Dockerfile . --tag dwk-log-output-reader:1.10.0`
- `k3d image import dwk-log-output-writer:1.10.0 dwk-log-output-reader:1.10.0`

## Edit `deployment.yaml` and `ingress.yaml`

I assign two containers in one yaml file : `log-output-deployment.yaml`. This allows me to launch two containers in the same pod. I also create a `emptyDir` volume and attach it to both of the containers.

```
...
spec:
  ...
  template:
    ...
    spec:
      volumes:
        - name: shared-image
          emptyDir: {}
      containers:
        - name: dwk-log-output-writer
          ...
          volumeMounts:
          - name: shared-image
            mountPath: /usr/src/app/files
        - name: dwk-log-output-reader
          ...
          volumeMounts:
          - name: shared-image
            mountPath: /usr/src/app/files
```

Since both applications `reader` and `writer` maintain the functionality of a simple web server that returns the current timestamp upon request, I had to assign different ports to each application. I use `7777` and `7778`. 

Thus, I edit my `ingress` and `service` as well, so that it can differentiate between requests for `reader` and `writer`. 

```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: dwk-log-output-ing
spec:
  rules:
  - http:
      paths:
      - path: /now/writer
        pathType: Prefix
        backend:
          service:
            name: dwk-log-output-svc
            port:
              number: 7777
      - path: /now/reader
        pathType: Prefix
        backend:
          service:
            name: dwk-log-output-svc
            port:
              number: 7778
```

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
    # service port 7777 -> container port 7777
    - port: 7777
      name: dwk-log-output-reader
      protocol: TCP
      targetPort: 7777 
    # service port 7778 -> container port 7778
    - port: 7778
      name: dwk-log-output-writer
      protocol: TCP
      targetPort: 7778
```

## Deploy and validate

- `kubectl apply -f manifests`

  ```
  ingress.networking.k8s.io/dwk-log-output-ing created
  deployment.apps/dwk-log-output created
  service/dwk-log-output-svc created
  deployment.apps/dwk-ping-pong created
  service/dwk-ping-pong-svc created
  ```

The reader's output tells us that everything is working as expected:
- `kubectl logs deployments/dwk-log-output dwk-log-output-reader -f`

  ```
  2025-01-28T20:40:56.603Z: eaa077d6-d21d-4fbb-be2e-5c940adddcf9
  INFO:     Started server process [1]
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://0.0.0.0:7778 (Press CTRL+C to quit)
  2025-01-28T20:41:01.605Z: 3a76ad1c-32e8-48c7-8ced-e8c1a7d46d4f
  2025-01-28T20:41:06.606Z: a5dd2187-0adb-422a-abf3-3bd2dba0c5bf
  2025-01-28T20:41:11.607Z: d46233c9-7e03-4abc-b057-f35ec8fdbe22
  2025-01-28T20:41:16.608Z: 5d3e2557-7db3-4559-9f8a-7840c1c58397
  2025-01-28T20:41:21.609Z: 586c3a2c-2deb-4681-9331-8c6b5a20c985
  ...
  ```

We can further inspect the contents of the shared file `timestamp.txt`, to see if the writer is actually doing its job:

Exec into running container:
- `kubectl exec -it deployments/dwk-log-output -c dwk-log-output-writer sh`

Inspect shared file `timestamp.txt`:

- `cat /usr/src/app/files/timestamp.txt `

  ```
  2025-01-28T20:40:56.603Z: eaa077d6-d21d-4fbb-be2e-5c940adddcf9
  2025-01-28T20:41:01.605Z: 3a76ad1c-32e8-48c7-8ced-e8c1a7d46d4f
  2025-01-28T20:41:06.606Z: a5dd2187-0adb-422a-abf3-3bd2dba0c5bf
  2025-01-28T20:41:11.607Z: d46233c9-7e03-4abc-b057-f35ec8fdbe22
  ...
  ```

The previously created endpoints are both alive in both applications as well.

- `curl 127.0.0.1:8081/now/reader`

  ```
  {"message":"2025-01-28T21:25:55.849Z: d07f6efd-7fa4-4dcd-a1b3-44b85ed496ba"}
  ```

- `curl 127.0.0.1:8081/now/writer`

  ```
  {"message":"2025-01-28T21:26:19.821Z: 6a2dbfa0-9690-49f7-b8f8-0277f8d6efb5"}
  ```
