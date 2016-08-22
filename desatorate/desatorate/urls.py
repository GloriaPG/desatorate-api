"""desatorate URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin
from rest_framework.routers import DefaultRouter

from api.viewsets import * # flake8: noqa

admin.autodiscover()

router = DefaultRouter()

router.register(r'login', LoginViewSet, base_name="login")
router.register(r'recover-password', RecoverPasswordViewSet,
                base_name="recover-password")
router.register(r'register', RegisterViewSet, base_name="register")

router.register(r'requests', RequestViewSet)
router.register(r'users', UserViewSet)
router.register(r'request-filter', RequestFilterViewSet)

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^api/v1/', include(router.urls)),
    url(r'^api/v1/api-token-verify/',
        'rest_framework_jwt.views.verify_jwt_token'
        ),
    url(r'^api/v1/api-token-refresh/',
        'rest_framework_jwt.views.refresh_jwt_token'),
    url(r'^api/v1/docs/', include('rest_framework_swagger.urls')),
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT, }),
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.MEDIA_ROOT, }),
]
