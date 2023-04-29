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

cd /root/texas-showdown/vue-project/
npm install
npm run build
mkdir -p /usr/share/nginx/localhost/html
cp -r dist/* /usr/share/nginx/localhost/html/
chown -R nginx:nginx /usr/share/nginx/localhost/html

echo "Writing to /etc/nginx/conf.d/localhost.conf..."
cat > /etc/nginx/conf.d/localhost.conf << EOF
server {
    root /usr/share/nginx/localhost/html;
    index index.html index.htm index.nginx-debian.html;

    server_name localhost www.localhost;

    location /texas_api/ {
        proxy_pass https://127.0.0.1:8443/;
    }
    location /socket.io/ {
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$host;
        proxy_pass https://127.0.0.1:8443/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    listen 443 ssl;
    ssl_certificate /root/certs/self-signed.crt;
    ssl_certificate_key /root/certs/self-signed.key;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;
}
server {
    if ($host = localhost) {
        return 301 https://\$host\$request_uri;
    }

    listen 80;

    server_name localhost www.localhost;
    return 404;
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

useradd daphne

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

# change the database owner to daphne
chown daphne:daphne /usr/lib/texas/texas/db.sqlite3
chown daphne:daphne /usr/lib/texas/texas

systemctl daemon-reload
