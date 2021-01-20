"""please_marketing URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from please_marketing_app import views
from please_marketing_referral_program import views
from please_marketing_growth_hack import views
from please_marketing_landing_pages import views
from please_marketing_recommendation import views
from django.views.generic import RedirectView


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('please_marketing_app.urls')),
    url(r'parrainage/', include('please_marketing_referral_program.urls')),
    url(r'inscription/', include('please_marketing_growth_hack.urls')),
    url(r'ads/', include('please_marketing_landing_pages.urls')),
    url(r'jeux/', include('please_marketing_growth_hack.urls')),
    url(r'recommendation/', include('please_marketing_recommendation.urls')),
    url(r'favicon.ico$', RedirectView.as_view(url='https://s3.eu-west-3.amazonaws.com/pleasemarketing/static/please_marketing_referral_program/img/favicon/favicon.ico'))
]
