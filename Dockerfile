FROM robertdebock/rockylinux

ADD . /root/texas-showdown

RUN cd /root/texas-showdown && echo "production" | ./install.sh

# EXPOSE 8080 443
EXPOSE 80 443

CMD [ "/sbin/init" ]