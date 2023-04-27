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

dnf -y install python39
dnf -y install epel-release
dnf -y install certbot
dnf -y install nginx
dnf -y install python3-certbot-nginx

echo "Please enter the domain name for the server (example: example.com):"
read hostName

cd /root/texas-showdown/vue-project/
npm install
npm run build
mkdir -p /usr/share/nginx/$hostName/html
cp -r dist/* /usr/share/nginx/$hostName/html/
chown -R nginx:nginx /usr/share/nginx/$hostName/html

echo "Writing to /etc/nginx/conf.d/$hostName.conf..."
cat > /etc/nginx/conf.d/$hostName.conf << EOF
server {
    listen 80;

    root /usr/share/nginx/$hostName/html;
    index index.html index.htm index.nginx-debian.html;

    server_name $hostName www.$hostName;

    location ~ ^/texas_api/?[A-Za-z0-9_./]*$ {
        proxy_pass https://127.0.0.1:8443;
    }
    location ~ ^/[A-Za-z0-9_./]*$ {
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

cp -r /root/texas-showdown/texas /usr/lib

echo "Installing requirements for django server in python virtual environment..."
cd /usr/lib/texas/
python3.9 -m venv env
source env/bin/activate
pip install -r requirements.txt

# generate a secret key for the django server
djangoSecretKey=$(python -c 'import string; import secrets; alphabet = string.ascii_letters + string.digits; print("".join(secrets.choice(alphabet) for i in range(64)))')

certbot --nginx -d $hostName

useradd daphne

mkdir /usr/lib/texas/texas/certs
cp /etc/letsencrypt/live/$hostName/privkey.pem /usr/lib/texas/texas/certs/privkey.pem
cp /etc/letsencrypt/live/$hostName/cert.pem /usr/lib/texas/texas/certs/cert.pem
chown daphne /usr/lib/texas/texas/certs/privkey.pem
chown daphne /usr/lib/texas/texas/certs/cert.pem

echo "Writing to /usr/lib/texas/texas/config.ini..."
cat > /usr/lib/texas/texas/config.ini << EOF
[django]
secret_key = $djangoSecretKey
is_development = false
hostname = $hostName
EOF

echo "Writing to /etc/systemd/system/daphne.service..."
cat > /etc/systemd/system/daphne.service << EOF
[Unit]
Description=Daphne service

[Service]
User=daphne
WorkingDirectory=/usr/lib/texas
ExecStart=/bin/bash -c 'cd /usr/lib/texas && source env/bin/activate && cd texas && daphne -e ssl:8443:privateKey=/usr/lib/texas/texas/certs/privkey.pem:certKey=/usr/lib/texas/texas/certs/cert.pem texas.asgi:application'

[Install]
WantedBy=multi-user.target
EOF

echo "Running migrations..."
cd texas
python manage.py migrate

systemctl daemon-reload
systemctl enable daphne
systemctl restart daphne
systemctl enable nginx
systemctl restart nginx