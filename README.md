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

## First-time setup

Ensure the latest version of nodejs 16 is installed on the server. On Rocky Linux 8, install by running the following as root:
```
dnf module reset nodejs
dnf module install nodejs:16
```

Ensure httpd is installed on the server. On Rocky Linux 8, install by running the following as root:
```
dnf install httpd
```

Create the file `/etc/httpd/conf.d/texas.conf` and make it have the following contents, replacing XX.XX.XX.XX with the server's IP:
```
<VirtualHost XX.XX.XX.XX:80>
    DocumentRoot "/var/www/html/dist/"
</VirtualHost>
```

On the server, run the following as root from the /root directory:
```
git clone https://github.com/HannahLilyW/texas-showdown.git
cd texas-showdown/vue-project/
npm install
npm run build
cp -r dist /var/www/html/
systemctl restart httpd
cd /root/texas-showdown/texas/
```

## Subsequent updates

Run the following as root:

```
cd /root/texas-showdown/
git pull
cd vue-project/
npm run build
cp -r dist /var/www/html/
systemctl restart httpd
```
