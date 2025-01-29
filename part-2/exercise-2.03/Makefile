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
