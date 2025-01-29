# Requirements

Create a namespace for the project and move everything related to the project to that namespace.

# Solution

## Create namespace

- `kubectl create namespace project`

    ```
    namespace/project created
    ```

- `kubectl get namespaces`

    ```
    NAME              STATUS   AGE
    default           Active   19h
    exercise          Active   34m
    kube-node-lease   Active   19h
    kube-public       Active   19h
    kube-system       Active   19h
    project           Active   11s
    ```

Like in the previous exercise, I remove everything from the cluster, then re-create everything with a namespace specified.

I copy my manifests from the previous exercises and run `kubectl delete -f manifests/`. 

```

deployment.apps "dwk-project" deleted
ingress.networking.k8s.io "dwk-material-ingress" deleted
persistentvolume "example-pv" deleted
persistentvolumeclaim "image-claim" deleted
service "dwk-project-svc" deleted
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

- `kubectl apply -f manifests/ -n project`

Let's see if it did the magic:

- `kubectl get deploy`
    ```
    No resources found in default namespace.
    ```

- `kubectl get deploy -n project`
    ```
    NAME          READY   UP-TO-DATE   AVAILABLE   AGE
    dwk-project   0/1     1            0           72s
    ```

- `kubectl get pods`

    ```
    No resources found in default namespace.
    ```

- `kubectl get pods -n exercise`

    ```
    NAME                           READY   STATUS    RESTARTS   AGE
    dwk-project-7cf9fbfcfd-njlsr   0/2     Pending   0          98s
    ```

All my resources have been recreated at namespace `exercise`.

## Exception : Persistent Volums

Kubernetes Persistent Volumes exist across namespaces. 


- `kubectl get pv -n default`

    ```
    NAME         CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                  STORAGECLASS    VOLUMEATTRIBUTESCLASS   REASON   AGE
    example-pv   1Gi        RWO            Retain           Bound    exercise/image-claim   my-example-pv   <unset>                          8m34s
    ```
- `kubectl get pv -n exercise`

    ```
    NAME         CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                  STORAGECLASS    VOLUMEATTRIBUTESCLASS   REASON   AGE
    example-pv   1Gi        RWO            Retain           Bound    exercise/image-claim   my-example-pv   <unset>                          8m39s
    ```
- `kubectl get pv -n project `

    ```
    NAME         CAPACITY   ACCESS MODES   RECLAIM POLICY   STATUS   CLAIM                  STORAGECLASS    VOLUMEATTRIBUTESCLASS   REASON   AGE
    example-pv   1Gi        RWO            Retain           Bound    exercise/image-claim   my-example-pv   <unset>                          8m42s
    ```

All resources have been migrated to namespace `project`!