from django.urls import path
from please_marketing_recommendation import views


urlpatterns = [
    path('recommendation', views.recommendation, name='recommendation'),
]
