deploy:
	@docker build . --tag dwk-project:1.12.0
	@k3d image import dwk-project:1.12.0
	@kubectl delete -f manifests/
	@kubectl apply -f manifests/
	@sleep 5
	@kubectl get deployments
	@kubectl get services
	@kubectl get pods
