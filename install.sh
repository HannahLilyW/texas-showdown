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

# This should get the server's IP
ipAddress=$(ip addr show eth0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1 | head -1)

cat > /etc/httpd/conf.d/texas.conf << EOF
<VirtualHost $ipAddress:80>
    DocumentRoot "/var/www/html/dist/"
</VirtualHost>
EOF

cd /root/texas-showdown/vue-project/
npm install
npm run build
cp -r dist /var/www/html/

cp -r /root/texas-showdown/texas /usr/lib

# generate a secret key for the django server
djangoSecretKey=$(python -c 'import secrets; print(secrets.token_urlsafe())')

cat > /usr/lib/texas/config.ini << EOF
[django]
secret_key = "$djangoSecretKey"
EOF

# create django user
useradd django

# create systemd service file for django server
cat > /etc/systemd/system/texas.service << EOF
[Unit]
Description=Texas Showdown Django Rest Framework service

[Service]
User=django
WorkingDirectory=/usr/lib/texas
ExecStart=/bin/bash -c 'cd / && source env/bin/activate && python manage.py runserver'

[Install]
WantedBy=multi-user.target
EOF

# install the requirements for the django server in a python virtual environment
cd /usr/lib/texas/
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt

cd texas
python manage.py migrate

systemctl daemon-reload
systemctl enable httpd
systemctl enable texas
systemctl restart httpd
systemctl restart texas
