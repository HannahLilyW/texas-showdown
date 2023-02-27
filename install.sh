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
    dnf module reset nodejs
    dnf module install nodejs:16
fi

dnf install httpd
dnf install python39
dnf install python39-mod_wsgi

# This should get the server's IP
ipAddress=$(ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1 | head -1)

echo "Writing to /etc/httpd/conf.d/texas.conf..."
cat > /etc/httpd/conf.d/texas.conf << EOF
<VirtualHost $ipAddress:80>
    DocumentRoot "/var/www/html/dist/"
</VirtualHost>

WSGIScriptAlias /texas_api /usr/lib/texas/texas/texas/wsgi.py
WSGIPythonHome /usr/lib/texas/env
WSGiPythonPath /usr/lib/texas/texas

<Directory /usr/lib/texas/texas/texas>
<Files wsgi.py>
Require all granted
</Files>
</Directory>
EOF

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

echo "Writing to /usr/lib/texas/texas/config.ini..."
cat > /usr/lib/texas/texas/config.ini << EOF
[django]
secret_key = "$djangoSecretKey"
EOF

echo "Running migrations..."
cd texas
python manage.py migrate

# create django user
useradd django

systemctl daemon-reload
systemctl enable httpd
systemctl restart httpd
