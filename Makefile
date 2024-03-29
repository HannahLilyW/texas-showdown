# Build the container (Should only need to do this once unless the Dockerfile changes.)
docker-build:
	docker build -t texas .

# Create and initialize the container
docker-run:
	sudo docker run -dit --tty -v /sys/fs/cgroup:/sys/fs/cgroup:ro --privileged -p 80:80 -p 443:443 --name texas texas

# Run the development install script inside the container
docker-install:
	sudo docker exec -it texas bash -c "/root/texas-showdown/devinstall.sh"

# Run the daphne daemon
docker-daphne:
	docker exec -dit texas bash -c "cd /usr/lib/texas && source env/bin/activate && cd texas && daphne -e ssl:8443:privateKey=/root/certs/self-signed.key:certKey=/root/certs/self-signed.crt texas.asgi:application"

# Run the nginx daemon
docker-nginx:
	docker exec -dit texas nginx

# Start a shell inside the container
docker-sh:
	docker exec -it texas bash

# Stop a running container
docker-stop:
	docker stop texas

# Remove a running container (does not remove the built image, no need to build the image again)
docker-rm:
	docker rm texas
