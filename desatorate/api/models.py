# -*- coding: utf-8 -*-
import os
from hashlib import md5
from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)

from django.db import models
from django.db.models.signals import post_save
from django.core.mail import EmailMultiAlternatives
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, Transpose


def upload_to_avatar(instance, filename):
    """
    Get the upload path to the profile image.
    """
    return '{0}/{1}{2}'.format(
        "avatars",
        md5(filename).hexdigest(),
        os.path.splitext(filename)[-1]
    )


class UserManager(BaseUserManager):
    """
    Custom manager for create users staff and superuser.
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Method for create new users.
        """
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            last_login=timezone.now(),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Creating new user staff.
        """
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Creating new user superuser.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Mapping table user desatorate.
    """
    gender_choices = (
        ("Mujer", 'Mujer'),
        ("Hombre", 'Hombre')
    )

    username = models.CharField(
        max_length=50,
        blank=False,
        null=False,
        unique=True
    )

    name = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    last_name = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    second_last_name = models.CharField(
        max_length=50,
        blank=True,
        null=True
    )

    avatar = models.ImageField(
        upload_to=upload_to_avatar,
        help_text="Elija imagen de logo (200x200)",
        verbose_name="Avatar",
        default="default.png"
    )

    avatar_thumbnail = ImageSpecField(
        source='avatar',
        processors=[Transpose(), ResizeToFill(200, 200)],
        format='PNG',
        options={'quality': 60}
    )
    phone = models.TextField(
        max_length=20,
        blank=True,
        null=True
    )

    email = models.EmailField(
        unique=True,
        null=False,
        blank=False
    )

    birthday = models.DateField(
        null=True
    )

    gender = models.IntegerField(
        null=True,
        choices=gender_choices
    )

    register_date = models.DateField(
        auto_now=True,
    )

    last_modify_date = models.DateField(
        auto_now_add=True
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_('is_active')
    )

    is_staff = models.BooleanField(
        default=False,
        verbose_name=_('is_staff')
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    class Meta:
        db_table = 'user'

    def __unicode__(self):
        return self.get_full_name()

    def get_full_name(self):
        """
        Return full name user:
             name last_name second_last_name
        """
        parts = [self.name, self.last_name, self.second_last_name]
        return ' '.join(filter(None, parts))

    def get_short_name(self):
        """
        Return short name user:
            name last_name
        """
        return self.name

    def email_user(self, subject, body, html=None, from_email=None, **kwargs):
        """
        Send an email to this user.

            Args:
                subject (str): The subject for the email message.
                body (str): Body for the email message. Must be plain txt.
                html (optional[str]): HTML formatted version of the body.
                    If provided, this version shall be appended to message as
                    an alternative. Defaults to None.
                from_email (optional[str]): Email address that shall be used
                    as the sender of the email message. If it is not provided,
                    then the message will be marked as sent from the address
                    specified in the ```DEFAULT_FROM_EMAIL``` setting.
                    Defaults to None.
                **kwargs: Arbitrary keyword arguments that shall be used to
                    instantiate the ```EmailMultiAlternatives``` class.

            Returns:
                bool: True if the message was successfully sent.
        """
        if not from_email and settings.DEFAULT_FROM_EMAIL:
            from_email = settings.DEFAULT_FROM_EMAIL

        message = EmailMultiAlternatives(
            subject, body, from_email, [self.email], **kwargs)

        if html is not None:
            message.attach_alternative(html, 'text/html')

        return message.send() > 0


class UserDevice(models.Model):
    user = models.ForeignKey(User, null=False)
    device_token = models.TextField(max_length=250, null=False, blank=False)
    device_os = models.TextField(max_length=20, null=False, blank=False)
    status = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_device'

    def __unicode__(self):
        return self.device_token


class Request(models.Model):
    name = models.CharField(
        max_length=50
    )

    last_name = models.CharField(
        max_length=50
    )

    second_last_name = models.CharField(
        max_length=50
    )

    email = models.EmailField(
        max_length=20
    )

    phone = models.TextField(
        max_length=20
    )

    request_date = models.DateTimeField(
        auto_now=True,
    )

    device_os = models.TextField(max_length=20, null=False, blank=False)

    user = models.ForeignKey(User, null=False)

    comment = models.CharField(
        max_length=500
    )

    status = models.BooleanField(
        default=True
    )

    class Meta:
        db_table = 'request'

    def __unicode__(self):
        return self.get_full_name()

    def get_full_name(self):
        """
        Return full name user:
             name last_name second_last_name
        """
        parts = [self.name, self.last_name, self.second_last_name]
        return ' '.join(filter(None, parts))


def after_insert_request(sender, instance, **kwargs):
    print "Envía correo de notificacion"

# register the signal
post_save.connect(after_insert_request, sender=Request, dispatch_uid=__file__)
