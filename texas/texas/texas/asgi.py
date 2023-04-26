"""
ASGI config for texas project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
import socketio
from texas.sio_server import sio_server

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'texas.settings')

application = socketio.ASGIApp(sio_server, get_asgi_application())
# application = get_asgi_application()
