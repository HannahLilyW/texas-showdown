FROM robertdebock/rockylinux

ADD . /root/texas-showdown

EXPOSE 80 443

CMD [ "/sbin/init" ]