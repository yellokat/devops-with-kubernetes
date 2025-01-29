# Requirements

Create a namespace for the applications in the exercises. Move the "Log output" and "Ping-pong" to that namespace and use that in the future for all of the exercises. You can follow the material in the default namespace.

# Solution

## Create namespace

- `kubectl create namespace exercise`

  ```
  namespace/exercise created
  ```

- `kubectl get namespaces`

  ```
  NAME              STATUS   AGE
  default           Active   18h
  exercise          Active   5s
  kube-node-lease   Active   18h
  kube-public       Active   18h
  kube-system       Active   18h
  ```

My plan is to remove everything from the cluster, then re-create everything with a namespace specified.

I copy my manifests from the previous exercises and run `kubectl delete -f manifests/`. 

```
ingress.networking.k8s.io "dwk-log-output-ing" deleted
deployment.apps "dwk-log-output" deleted
service "dwk-log-output-svc" deleted
persistentvolume "example-pv" deleted
persistentvolumeclaim "image-claim" deleted
deployment.apps "dwk-ping-pong" deleted
service "dwk-ping-pong-svc" deleted
```

Let's see if everything is gone:

- `kubectl get deploy`
  ```
  No resources found in default namespace.
  ```

- `kubectl get pods`
  ```
  No resources found in default namespace.
  ```

- `kubectl get ing`
  ```
  No resources found in default namespace.
  ```

- `kubectl get service`
  
  ```
  NAME         TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
  kubernetes   ClusterIP   10.43.0.1    <none>        443/TCP   19h
  ```

  This one is automatically created by kubernetes so I won't remove it.

Seems like everything is pretty much gone.

## Re-create resources with namespace specified

- `kubectl apply -f manifests/ -n exercise`

Let's see if it did the magic:

- `kubectl get deploy`
  ```
  No resources found in default namespace.
  ```

- `kubectl get deploy -n exercise`
  ```
  NAME             READY   UP-TO-DATE   AVAILABLE   AGE
  dwk-log-output   1/1     1            1           10s
  dwk-ping-pong    1/1     1            1           10s
  ```

- `kubectl get pods`

  ```
  No resources found in default namespace.
  ```
- `kubectl get pods -n exercise`

  ```
  NAME                             READY   STATUS    RESTARTS   AGE
  dwk-log-output-f875c5c9c-42zz4   2/2     Running   0          53s
  dwk-ping-pong-6ff7d4d7b6-x5slj   1/1     Running   0          53s
  ```

All my resources have been recreated at namespace `exercise`.
