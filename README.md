# texas-showdown
An implementation of the game Texas Showdown, created for the class SWE 681: Secure Software Design and Programming.

# Run frontend locally for development
Tested only on Windows
```
cd vue-project
npm run dev
```

# Run backend locally for development
Tested only on Windows
```
cd texas
env\Scripts\activate
cd texas
python manage.py migrate
python manage.py runserver
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
