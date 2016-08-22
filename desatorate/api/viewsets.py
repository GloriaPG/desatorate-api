# -*- encoding: utf-8 -*-

import hashlib

import os
import random
import string

from calendar import timegm
from datetime import datetime

from PIL import Image

from django.conf import settings
from django.contrib.auth import logout
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string


from rest_framework import (
    filters,
    status,
    viewsets
)

from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated

from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework_jwt.settings import api_settings

from .models import User
from .models import UserDevice
from .models import Request

from .serializers import *  # flake8: noqa

class RegisterViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def create(self, request, format=None):
        """
        Register user
        ---

        serializer: RegisterSerializer
        omit_serializer: false

        parameters_strategy: merge
        omit_parameters:
            - path
        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 201
              message: CREATED
            - code: 500
              message: INTERNAL SERVER ERROR

        consumes:
            - application/json
        produces:
            - application/json
        """
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():

            # Save user
            user = serializer.save(
                request=request,
                validated_data=serializer.validated_data)

            return Response(
                RegistrationResultSerializer(
                    user,
                    context={'request': request}
                ).data,
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RecoverPasswordViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def create(self, request, format=None):
        """
            Recover password.
            ---
            type:
              email:
                required: true
                type: string
            parameters:
                - name: email
                  description: Email user which try recover password.
                  required: true
                  type: string
                  paramType: form
            responseMessages:
                - code: 400
                  message: BAD REQUEST
                - code: 201
                  message: CREATED
                - code: 500
                  message: INTERNAL SERVER ERROR
            consumes:
                - application/json
            produces:
                - application/json
        """
        if 'email' in request.data:

            email = request.data['email']

            queryset = User.objects.filter(email=email, is_active=True)

            user = get_object_or_404(queryset)

            new_password = "".join(
                [random.choice(string.digits + string.letters) for i in xrange(5)])

            user.set_password(new_password)

            user.save()

            serializer = UserSerializer(user)

            context = {
                'name': user.name,
                'email': user.email,
                'password': new_password
            }

            # Gets the email subject in a single line.
            message_subject = render_to_string(
                'recover_password/recover_password_email_subject.txt',
                context
            )

            message_subject = ''.join(message_subject.splitlines())

            # Renders the plain text message.
            message_text = render_to_string(
                'recover_password/recover_password_email.txt',
                context
            )

            # Renders the html message.
            message_html = render_to_string(
                'recover_password/recover_password_email.html',
                context
            )

            try:
                user.email_user(message_subject, message_text, message_html)
            except Exception, e:
                return Response({'message': 'The email could not be sent.', 'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        else:
            return Response({'email': 'email is mandatory field.'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': u'Se ha enviado la contraseña.', 'email': serializer.data['email']}, status=status.HTTP_200_OK)

class LoginViewSet(viewsets.ViewSet):
    permission_classes = (AllowAny,)

    def create(self, request, format=None):
        """
        Login
        ---
        type:
          email:
            required: true
            type: string
          password:
            required: true
            type: string
          device_os:
            required: true
            type: string
          device_token:
            required: false
            type: string
        parameters:
            - name: email
              description: email user.
              required: true
              type: string
              paramType: form
            - name: password
              description: Password.
              required: true
              type: string
              paramType: form
            - name: device_os
              required: true
              description: Mobile operating system device user.
              type: string
              paramType: form
            - name: device_token
              description: Device token.
              required: false
              type: string
              paramType: form
        responseMessages:
            - code: 400
              message: BAD REQUEST
            - code: 200
              message: OK
            - code: 500
              message: INTERNAL SERVER ERROR
        consumes:
            - application/json
        produces:
            - application/json
        """

        login_serializer = LoginSerializer(data=request.data)

        if login_serializer.is_valid():

            # Init user object.
            user = None

            try:

                # Get user.
                user = User.objects.get(
                    email=request.data['email'],
                    is_active=True
                )

                # Check password.
                if not user.check_password(request.data['password']):

                    return Response(
                        {"non_field_errors": "Unable to login with provided credentials."},
                        status=status.HTTP_400_BAD_REQUEST)

            except Exception:
                return Response(
                    {"non_field_errors": "Unable to login with provided credentials."},
                    status=status.HTTP_400_BAD_REQUEST)

            # Create device
	        try:
	            device = UserDevice.objects.get(user=user)
	            device.device_token = validated_data.get(
	                'device_token',
	                None
	            ),
	            device.device_os = validated_data.get('device_os'),
	            device.status = True
	            device.save()
	        except UserDevice.DoesNotExist:
	            UserDevice(
	                user=user,
	                device_token=validated_data.get(
	                    'device_token',
	                    None
	                ),
	                device_os=validated_data.get('device_os'),
	                status=True
	            ).save()

            # Generate Token.
            jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
            jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
            payload = jwt_payload_handler(user)

            if api_settings.JWT_ALLOW_REFRESH:
                payload['orig_iat'] = timegm(
                    datetime.utcnow().utctimetuple()
                )

            # Token.
            token = jwt_encode_handler(payload)
            user_serializer = UserSerializer(user,context={'request': request})

            return Response({"token": token, "user": user_serializer.data},
                            status=status.HTTP_200_OK
                            )

        return Response(login_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RequestViewSet(viewsets.ModelViewSet):

    serializer_class = RequestSerializer
    queryset = Request.objects.all()

class UserViewSet(viewsets.ModelViewSet):

    serializer_class = UserSerializer
    queryset = User.objects.all()

class RequestFilterViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = RequestSerializer
    queryset = Request.objects.all()
    filter_backends = (filters.DjangoFilterBackend,
                       filters.OrderingFilter, filters.SearchFilter,)
    search_fields = (
        'name',
        'last_name',
        'second_last_name',
        'comment'
    )
    ordering_fields = '__all__'
    filter_fields = (
        'id',
        'name',
        'last_name',
        'second_last_name',
        'user__id',
        'user__email',
        'request_date',
        'status'
    )