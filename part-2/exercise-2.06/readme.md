# Requirements

Use the official Kubernetes documentation for this exercise.

- https://kubernetes.io/docs/concepts/configuration/configmap/ and
- https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/
should contain everything you need.

Create a ConfigMap for the "Log output" application. The ConfigMap should define one file information.txt and one env variable MESSAGE.

The app should map the file as a volume, and set the environment variable and print the content of those besides the usual output:
```
file content: this text is from file
env variable: MESSAGE=hello world
2024-03-30T12:15:17.705Z: 8523ecb1-c716-4cb6-a044-b9e83bb98e43.
Ping / Pongs: 3
```
# Solution

## Create configmap 

```
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-configmap
data:
  # property-like key; each key maps to a simple value
  MESSAGE: "hello world"

  # file-like key
  information.txt: |
    this text is from file
```

## Mount the configmap as a volume

I will mount the created configmap as a volume on containers `log-output-writer` and `log-output-reader`.

- First I add the configmap as a pod-level volume:
  ```
  ...
  volumes:
    - name: shared-image
      persistentVolumeClaim:
        claimName: image-claim
    - name: exercise-configmap
      configMap:
        name: example-configmap
  ...
  ```

- Then I mount the volume into my desired container.

  ```
  - name: dwk-log-output-writer
    image: dwk-log-output-writer:2.6.0
    imagePullPolicy: Never
    env:
      - name: PORT
        value: "7777"
      - name: MESSAGE
        valueFrom:
          configMapKeyRef:
            name: example-configmap
            key: MESSAGE
    volumeMounts:
    - name: shared-image
      mountPath: /usr/src/app/files
    - name: exercise-configmap
      mountPath: "/usr/src/app/config"
      readOnly: true
  ```

  Note that I have additionally created an environment variable MESSAGE using the `env[].valueFrom.configMapKeyRef` field. [Reference link](https://kubernetes.io/docs/concepts/configuration/configmap/#using-configmaps-as-environment-variables) is available here.

## Validate mounted configmap

First, I make sure to use the namespace `exercise`:
- `kubens exercise`

    ```
    Active namespace is "exercise".
    ```

- I deploy the cluster using `make up`. It runs a subset of commands from `make deploy`.
    ```
    configmap/example-configmap created
    ingress.networking.k8s.io/dwk-log-output-ing created
    deployment.apps/dwk-log-output created
    service/dwk-log-output-svc created
    persistentvolume/example-pv created
    persistentvolumeclaim/image-claim created
    deployment.apps/dwk-ping-pong created
    service/dwk-ping-pong-svc created
    ```

I exec into a `log-output` container and see if my configmap exists, in the form of a file and an environment variable.

- `kubectl exec -it deployments/dwk-log-output -c dwk-log-output-reader sh`

    ```
    /usr/src/app # cat config/information.txt 
    this text is from file
    ```
    ```
    /usr/src/app # echo $MESSAGE
    hello world
    ```

    The mounted file exists, and the environment variable is set.

## Modify the application

I modify my application so that it reads values from the file and environment variable and return them as a string.

```
MESSAGE = os.environ["MESSAGE"]
...
@app.get("/now/reader", response_class=PlainTextResponse)
def read_root():
    with open(os.path.join('config', 'information.txt'), 'r') as f:
        text_from_file = f.readline()
    stringbuilder = ""
    stringbuilder += f"file content: {text_from_file}\n"
    stringbuilder += f"env variable: MESSAGE={MESSAGE}\n"
    stringbuilder += f"{get_current_timestamp()}.\n"
    stringbuilder += f"\nPing / Pongs : {get_pings()}"
    return stringbuilder
```

I run `make deploy` to re-apply the changes I made.

## Validation

- `curl 127.0.0.1:8081/now/reader`

    ```
    file content: this text is from file
    env variable: MESSAGE=hello world
    2025-01-29T23:42:50.070Z: 434afb13-e664-40a6-b231-396e0f456793.
    Ping / Pongs : 0
    ```
- `curl 127.0.0.1:8081/now/writer`

    ```
    file content: this text is from file
    env variable: MESSAGE=hello world
    2025-01-29T23:43:08.841Z: 1a49ca95-6bdd-4245-aba9-4e27095ff286.
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
    file content: this text is from file
    env variable: MESSAGE=hello world
    2025-01-29T23:43:40.031Z: b81843d9-2237-42f7-8199-9e9b0ff80586.
    Ping / Pongs : 3
    ```
- `curl 127.0.0.1:8081/now/writer`

    ```
    file content: this text is from file
    env variable: MESSAGE=hello world
    2025-01-29T23:43:53.568Z: 194d5b81-f46f-49d4-9190-504adc6cebe9.
    Ping / Pongs : 3
    ```

Functionality verified!