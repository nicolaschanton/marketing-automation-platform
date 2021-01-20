from django.urls import path
from please_marketing_referral_program import views


urlpatterns = [
    path('parrainage', views.referral, name='referral'),
    path('parrainage_sms', views.referral_sms, name='referral_sms'),
    path('parrainage_email', views.referral_email, name='referral_email'),
    path('parrainage_login', views.referral_login, name='parrainage_login'),
    path('hello', views.hello, name='hello'),
]
