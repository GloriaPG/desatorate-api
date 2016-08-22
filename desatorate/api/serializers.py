# -*- coding: utf-8 -*-
from calendar import timegm
from datetime import datetime

from rest_framework import serializers

from rest_framework_jwt.settings import api_settings

from .models import User
from .models import UserDevice
from .models import Request

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER


class RegisterSerializer(serializers.ModelSerializer):

    device_token = serializers.CharField(
        max_length=250,
        allow_blank=False,
        trim_whitespace=False
    )
    device_os = serializers.CharField(
        max_length=7,
        allow_blank=False,
        trim_whitespace=True
    )

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'name',
            'last_name',
            'second_last_name',
            'phone',
            'email',
            'birthday',
            'gender',
            'password',
            'username',
            'device_token',
            'device_os'
        )

    def save(self, request, validated_data):
        """
        Create register in table's user and register.
        """
        # Create user
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['username'].encode('utf-8')
        )

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

        return user


class RegistrationResultSerializer(serializers.ModelSerializer):
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'name',
            'last_name',
            'second_last_name',
            'avatar',
            'phone',
            'email',
            'birthday',
            'gender',
            'register_date',
            'last_modify_date',
            'is_active',
            'is_superuser',
            'is_staff',
            'token'
        )

    def get_token(self, obj):
        """
        Create token to user when user register.
        """

        user = User.objects.get(email=obj.email)

        payload = jwt_payload_handler(user)

        if api_settings.JWT_ALLOW_REFRESH:
            payload['orig_iat'] = timegm(
                datetime.utcnow().utctimetuple()
            )

        token = jwt_encode_handler(payload)

        return token


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'name',
            'last_name',
            'second_last_name',
            'avatar',
            'phone',
            'email',
            'password',
            'birthday',
            'gender',
            'register_date',
            'last_modify_date',
            'is_active',
            'is_superuser',
            'is_staff'
        )


class RequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = Request
        fields = (
            'id',
            'name',
            'last_name',
            'second_last_name',
            'phone',
            'email',
            'request_date',
            'device_os',
            'user',
            'comment',
            'status'
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    device_os = serializers.CharField(max_length=50, required=True)
    device_token = serializers.CharField(max_length=250, required=False)


class UserDeviceSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserDevice
        fields = (
            'id',
            'user',
            'device_token',
            'device_os',
            'status'
        )
