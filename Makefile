# Build the container (Should only need to do this once unless the Dockerfile changes.)
docker-build:
	docker build -t texas .

# Run the container (Just kill the terminal once it hangs)
docker-run:
	docker run -d --tty -v /sys/fs/cgroup:/sys/fs/cgroup:ro --privileged -p 80:80 -p 443:443 --name texas texas

# Run the development install script inside the container
docker-install:
	docker exec -it texas bash -c "/root/texas-showdown/devinstall.sh"

# Start a shell inside the container
docker-sh:
	docker exec -it texas bash

# Stop a running container
docker-stop:
	docker stop texas

# Remove a running container (does not remove the built image, no need to build the image again)
docker-rm:
	docker rm texas
