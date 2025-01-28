# Requirements

Use a NodePort Service to enable access to the project.

# Solution

## Setting up the cluster again with port mappings

I first delete the existing cluster with `k3d cluster delete`.
```
INFO[0000] Deleting cluster 'k3s-default'               
INFO[0001] Deleting 1 attached volumes...               
INFO[0001] Removing cluster details from default kubeconfig... 
INFO[0001] Removing standalone kubeconfig file (if there is one)... 
INFO[0001] Successfully deleted cluster k3s-default!
``` 
Then I set up the cluster again with `k3d cluster create --port 8082:30080@agent:0 -p 8081:80@loadbalancer --agents 2`:
```
...
INFO[0018] Cluster 'k3s-default' created successfully!  
INFO[0018] You can now use it like this:                
kubectl cluster-info
```

Now any requests made to the local port `8082` will be forwarded to port `30080` of `agent 1`.

## Deploy application to cluster

First, I rebuild my docker image.
- `docker build . --tag dwk-project:1.6.0`

Then I import this into the newly created cluster.
- `k3d image import dwk-project:1.6.0`

  ```
  INFO[0000] Importing image(s) into cluster 'k3s-default' 
  INFO[0000] Saving 1 image(s) from runtime...            
  INFO[0002] Importing images into nodes...               
  INFO[0002] Importing images from tarball '/k3d/images/k3d-k3s-default-images-20250128215829.tar' into node 'k3d-k3s-default-server-0'... 
  INFO[0002] Importing images from tarball '/k3d/images/k3d-k3s-default-images-20250128215829.tar' into node 'k3d-k3s-default-agent-1'... 
  INFO[0002] Importing images from tarball '/k3d/images/k3d-k3s-default-images-20250128215829.tar' into node 'k3d-k3s-default-agent-0'... 
  INFO[0005] Removing the tarball(s) from image volume... 
  INFO[0006] Removing k3d-tools node...                   
  INFO[0006] Successfully imported image(s)               
  INFO[0006] Successfully imported 1 image(s) into 1 cluster(s) 
  ```
I launch the deployment again:
- `kubectl apply -f manifests/deployment.yaml`

Let's see if everything is working so far.
- `kubectl get deployments`

  ```
  NAME          READY   UP-TO-DATE   AVAILABLE   AGE
  dwk-project   1/1     1            1           5m24s
  ```
- `kubectl logs deployments/dwk-project`

  ```
  INFO:     Started server process [1]
  INFO:     Waiting for application startup.
  INFO:     Application startup complete.
  INFO:     Uvicorn running on http://0.0.0.0:7777 (Press CTRL+C to quit)
  ```
## Writing service.yaml

I create a new service in the cluster. Its type is `NodePort` and it will intercept ***all requests sent to all nodes at a certain port*** to a configurable `targetPort`.

```
apiVersion: v1
kind: Service
metadata:
  name: dwk-project-svc
spec:
  type: NodePort
  selector:
    app: dwk-project # This is the app as declared in the deployment.
  ports:
    - name: http
      nodePort: 30080 # Any request sent to all nodes in the cluster at port 30080 will be forwarded to targetPort
      protocol: TCP
      port: 7777 # Any request sent to this service at port 7777 will be forwarded to targetPort
      targetPort: 7777 # This is the target port
```

- I set `NodePort` to `30080`. Any request sent to `<anyNode>:30080` will be intercepted by this service.
- My application server listens to requests at port `7777`. Therefore I set `targetPort` to `7777`.
- Although `port` is not used in this exercise since we are working with nodeports, as common practice for convenience, `port` is generally assigned to the same number as `targetPort`. I set `port` to `7777`.

I finally launch this service with `kubectl apply`.
- `kubectl apply -f manifests/service.yaml`

  ```
  service/dwk-project-svc created
  ```

If all is set up well, 
- Requests made to `localhost:8082` will be forwarded to port `30080` at node `agent:0`.
- Then, our `NodePort` service will listen to that port `30080` and forward it to port `7777` of our server container inside the pod.

Let's see if our setup works as intended.
- `curl 127.0.0.1:8082/health-check`

  ```
  {"message":"OK"}
  ```

