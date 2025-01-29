build:
	@docker build -f log-output-reader.Dockerfile . --tag dwk-log-output-reader:2.6.0
	@docker build -f log-output-writer.Dockerfile . --tag dwk-log-output-writer:2.6.0
	@docker build -f ping-pong.Dockerfile . --tag dwk-ping-pong:2.6.0 && echo "\n"
	@k3d image import dwk-log-output-reader:2.6.0 dwk-log-output-writer:2.6.0 dwk-ping-pong:2.6.0 && echo "\n"
up:
	@kubectl apply -f manifests/ && echo "\n"

down:
	@kubectl delete -f manifests/ && echo "\n"

logs:
	@kubectl get deployments && echo "\n"
	@kubectl get services && echo "\n"
	@kubectl get pods

deploy:
	$(MAKE) build
	$(MAKE) down
	$(MAKE) up
	@sleep 5
	$(MAKE) logs
