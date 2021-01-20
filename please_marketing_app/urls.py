from django.urls import path
from please_marketing_app import views


urlpatterns = [
    path('', views.index, name='index'),
    path('index', views.index, name='index'),
    path('home', views.index, name='index'),
    path('webhook_intercom_events', views.webhook_intercom_events, name='webhook_intercom_events'),
    path('webhook_nps', views.webhook_nps, name='webhook_nps'),
    path('delivery_men_leads', views.delivery_men_leads, name='delivery_men_leads'),
    path('api/trigger_ie_30/', views.trigger_ie_30, name='trigger_ie_30'),
    path('api/get_neighborhood_open/<mw_nbid>/', views.get_neighborhood_open, name='get_neighborhood_open')
]
