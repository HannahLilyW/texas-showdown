if [[ ! -d "/root/texas-showdown" ]]
then
    echo "Directory /root/texas-showdown does not exist."
    echo "Please clone the project and run the install script before running this script."
    exit
fi

if [[ ! -e "/root/texas-showdown/hostname.txt" ]]
then
    echo "Please enter the domain name for the server (example: example.com):"
    read hostName
    touch /root/texas-showdown/hostname.txt
    echo $hostName > /root/texas-showdown/hostname.txt
else
    hostName=`cat hostname.txt`
fi

cd /root/texas-showdown/vue-project/
npm run build
rm -rf /usr/share/nginx/$hostName/html/*
cp -r dist/* /usr/share/nginx/$hostName/html/

cp -r /root/texas-showdown/texas /usr/lib
cd /usr/lib/texas/
source env/bin/activate
cd texas
python manage.py migrate

systemctl restart daphne
systemctl restart nginx
