if [[ ! -d "/root/texas-showdown" ]]
then
    echo "Directory /root/texas-showdown does not exist."
    echo "Please run cd /root && git clone https://github.com/HannahLilyW/texas-showdown.git before running this script."
    exit
fi

# Check if nodejs is already installed and on correct version
nodeVersion=$(node -v)
if [[ $nodeVersion = v16* ]] 
then
    echo "Node is already installed and on correct version (16)"
else
    echo "Node v16 doesn't seem to be installed. Attempting to install..."
    dnf -y module reset nodejs
    dnf -y module install nodejs:16
fi

dnf -y install httpd
dnf -y install python39
dnf -y install python39-mod_wsgi
dnf -y install epel-release
dnf -y install certbot
dnf -y install python3-certbot-apache
dnf -y install mod_ssl

# This should get the server's IP
# ipAddress=$(ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1 | head -1)

cd /root/texas-showdown/vue-project/
npm install
npm run build
cp -r dist /var/www/html/

cp -r /root/texas-showdown/texas /usr/lib

echo "Installing requirements for django server in python virtual environment..."
cd /usr/lib/texas/
python3.9 -m venv env
source env/bin/activate
pip install -r requirements.txt

# generate a secret key for the django server
djangoSecretKey=$(python -c 'import string; import secrets; alphabet = string.ascii_letters + string.digits; print("".join(secrets.choice(alphabet) for i in range(64)))')

echo "Writing to /etc/httpd/conf.d/texas.conf..."
cat > /etc/httpd/conf.d/texas.conf << EOF
<VirtualHost *:443>
ServerName localhost
DocumentRoot "/var/www/html/dist/"
SSLCertificateFile /root/certs/self-signed.crt
SSLCertificateKeyFile /root/certs/self-signed.key
Include /etc/letsencrypt/options-ssl-apache.conf
</VirtualHost>
<Directory /var/www/html/dist>
<IfModule mod_rewrite.c>
  RewriteEngine On
  RewriteBase /
  RewriteRule ^index\.html$ - [L]
  RewriteCond %{REQUEST_FILENAME} !-f
  RewriteCond %{REQUEST_FILENAME} !-d
  RewriteRule . /index.html [L]
</IfModule>
</Directory>

SSLProxyEngine on
ProxyPass "/socket.io/" "https://localhost/texas_api/socket.io/"

WSGIScriptAlias /texas_api /usr/lib/texas/texas/texas/wsgi.py
WSGIPythonHome /usr/lib/texas/env
WSGIPythonPath /usr/lib/texas/texas
WSGIPassAuthorization On

<Directory /usr/lib/texas/texas/texas>
<Files wsgi.py>
Require all granted
</Files>
</Directory>
EOF

echo "Writing to /etc/letsencrypt/options-ssl-apache.conf..."
cat > /etc/letsencrypt/options-ssl-apache.conf << EOF
SSLEngine on

SSLProtocol             all -SSLv2 -SSLv3 -TLSv1 -TLSv1.1
SSLCipherSuite          ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384
SSLHonorCipherOrder     off
SSLSessionTickets       off

SSLOptions +StrictRequire

# Add vhost name to log entries:
LogFormat "%h %l %u %t \"%r\" %>s %b \"%{Referer}i\" \"%{User-agent}i\"" vhost_combined
LogFormat "%v %h %l %u %t \"%r\" %>s %b" vhost_common
EOF

mkdir -p /root/certs/
openssl req -x509 -nodes -newkey rsa:2048 -days 3650 -keyout /root/certs/self-signed.key -out /root/certs/self-signed.crt

echo "Writing to /usr/lib/texas/texas/config.ini..."
cat > /usr/lib/texas/texas/config.ini << EOF
[django]
secret_key = $djangoSecretKey
is_development = true
hostname = localhost
EOF

echo "Running migrations..."
cd texas
python manage.py migrate

# change the database owner to apache
# and permanently change the selinux file context of the database and the directory it's in so apache is allowed to write to it
chown apache:apache /usr/lib/texas/texas/db.sqlite3
chown apache:apache /usr/lib/texas/texas
# semanage fcontext -a -t httpd_sys_rw_content_t /usr/lib/texas/texas/db.sqlite3
# semanage fcontext -a -t httpd_sys_rw_content_t /usr/lib/texas/texas
# restorecon -RF /usr/lib/texas/texas

systemctl daemon-reload
systemctl enable httpd
systemctl restart httpd
