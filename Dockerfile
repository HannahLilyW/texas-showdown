FROM robertdebock/rockylinux

ADD . /root/texas-showdown

EXPOSE 443

CMD [ "/sbin/init" ]
