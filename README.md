# texas-showdown
A fun card game

# Local development on windows

See vue-project/README.md for local frontend development

# Local development on ubuntu

This hasn't been tested in a while.

```
# Build the container (Should only need to do this once unless the Dockerfile changes.)
make docker-build

# Create and initialize the container
make docker-run

# Run the development install script inside the container (Just press enter through the openssl prompts)
make docker-install

# Run the httpd daemon
make docker-httpd

# Start a shell inside the container
make docker-sh

# Stop a running container
make docker-stop

# Remove a running container (does not remove the built image, no need to build the image again)
make docker-rm
```

# Update production environment

Tested only on Rocky Linux 8

## First-time setup

Follow the steps here for initial setup: https://www.digitalocean.com/community/tutorials/initial-server-setup-with-rocky-linux-8

Run the following as root on the server:
```
cd /root
git clone https://github.com/HannahLilyW/texas-showdown.git
cd texas-showdown
./install.sh
```

## Subsequent updates

Run the following as root:

```
cd /root/texas-showdown/
git pull
./update.sh
```

# Authentication
The site uses the TokenAuthentication scheme provided by Django REST Framework. For more info see https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication

TokenAuthentication is better than SessionAuthentication because SessionAuthentication is vulnerable to CSRF attacks. See https://stackoverflow.com/questions/54169145/django-rest-framework-session-auth-vs-token-auth-csrf for more info.
