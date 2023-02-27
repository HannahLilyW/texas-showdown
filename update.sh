if [[ ! -d "/root/texas-showdown" ]]
then
    echo "Directory /root/texas-showdown does not exist."
    echo "Please clone the project and run the install script before running this script."
    exit
fi

cd /root/texas-showdown/vue-project/
npm run build
rm -rf /var/www/html/dist
cp -r dist /var/www/html/

cp -r /root/texas-showdown/texas /usr/lib
cd /usr/lib/texas/
source env/bin/activate
cd texas
python manage.py migrate

systemctl restart httpd
systemctl restart texas
