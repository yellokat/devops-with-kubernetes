deploy:
	@docker build -f todo_app.Dockerfile . --tag todo-app:2.2.0 && echo "\n"
	@docker build -f todo_backend.Dockerfile . --tag todo-backend:2.2.0 && echo "\n"
	@k3d image import todo-app:2.2.0 todo-backend:2.2.0 && echo "\n"
	@kubectl delete -f manifests/ && echo "\n"
	@kubectl apply -f manifests/ && echo "\n"
	@sleep 5
	@kubectl get deployments && echo "\n"
	@kubectl get services && echo "\n"
	@kubectl get pods
