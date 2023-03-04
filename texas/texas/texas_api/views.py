from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import views, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from texas.logging import log
import json
import re


class CreateAccountView(views.APIView):
    # Endpoint for creating new accounts.

    # This endpoint is available to anyone, including unauthenticated users.
    permission_classes = [permissions.AllowAny]

    def post(self, request, format=None):
        if request.content_type != 'application/json':
            return Response('Content-Type must be application/json', status=status.HTTP_400_BAD_REQUEST)

        # If we get here, then Django REST Framework has already validated that request.data is valid json and has parsed it into a dict.

        username = request.data.get('username', None)
        password = request.data.get('password', None)

        # Validation
        if not isinstance(username, str):
            print(username)
            print(type(username))
            return Response('Username must be a string', status=status.HTTP_400_BAD_REQUEST)
        if not isinstance(password, str):
            return Response('Password must be a string', status=status.HTTP_400_BAD_REQUEST)
        if len(username) > 150:
            return Response('Username must be 150 characters or fewer', status=status.HTTP_400_BAD_REQUEST)
        if len(password) > 150:
            return Response('Password must be 150 characters or fewer', status=status.HTTP_400_BAD_REQUEST)
        if len(username) < 1:
            return Response('Username must be at least 1 character', status=status.HTTP_400_BAD_REQUEST)
        if len(password) < 8:
            return Response('Password must be at least 8 characters', status=status.HTTP_400_BAD_REQUEST)
        if not re.match(r'^[A-Za-z0-9_]+$', username):
            return Response('Username may only contain letters, digits, and underscores', status=status.HTTP_400_BAD_REQUEST)
        if not re.match(r'^[A-Za-z0-9_!@#$%^&*()]+$', password):
            return Response('Password may only contain letters, digits, and the following characters: _ ! @ # $ % ^ & * ( )', status=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).first() is not None:
            return Response('There is already a user with that username. Please choose another.', status=status.HTTP_400_BAD_REQUEST)
        try:
            # Run the password through the validators configured in AUTH_PASSWORD_VALIDATORS in settings.py
            validate_password(password)
        except ValidationError as e:
            # If the exception has type ValidationError, we know the error will have safe error messages from the built-in Django password validators.
            # Pass these back to the client so they know what to change about the password.
            return Response(f'Invalid password: {e}', status=status.HTTP_400_BAD_REQUEST)

        # Validation complete.

        try:
            user = User.objects.create(username=username, password=password)
        except Exception as e:
            log.error(f'Error creating account: Unexpected error creating user object: {e}')
            return Response('Error creating account', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        token = Token.objects.create(user=user)

        return Response({
            'token': token.key,
            'user_id': user.pk
        })
