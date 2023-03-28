# texas-showdown
An implementation of the game Texas Showdown, created for the class SWE 681: Secure Software Design and Programming.

# Windows development

## Run frontend locally for development
Tested only on Windows
```
cd vue-project
npm run dev
```

## Run backend locally for development
Tested only on Windows
```
cd texas
env\Scripts\activate
cd texas
python manage.py migrate
python manage.py runserver
```

# Docker development
Tested on Ubuntu
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

# Where to find backend logs
Backend error logs are saved at `/var/log/httpd/error_log`

# Authentication
The site uses the TokenAuthentication scheme provided by Django REST Framework. For more info see https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication

TokenAuthentication is better than SessionAuthentication because SessionAuthentication is vulnerable to CSRF attacks. See https://stackoverflow.com/questions/54169145/django-rest-framework-session-auth-vs-token-auth-csrf for more info.
