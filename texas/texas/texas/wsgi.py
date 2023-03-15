"""
WSGI config for texas project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

import socketio
from texas.sio_server import sio_server

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'texas.settings')

application = socketio.WSGIApp(sio_server, get_wsgi_application())
