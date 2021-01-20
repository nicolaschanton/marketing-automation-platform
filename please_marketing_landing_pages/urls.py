from django.urls import path
from please_marketing_landing_pages import views


urlpatterns = [
    path('lpa', views.lp_alert, name='lpa'),
    path('lpad', views.lp_alert_done, name='lpad'),
    path('lps', views.lp_signup, name='lps'),
    path('lp', views.lp, name='lp'),
    path('merci', views.thanks, name='thanks'),
    path('unsubscribe', views.unsubscribe, name='unsubscribe'),
    path('redirect_to_store_ranking', views.redirect_to_store_ranking, name='redirect_to_store_ranking'),
    path('game_play/<sharable_id>', views.please_game_play, name='please_game_play'),
    path('game/<sharable_id>', views.please_game, name='please_game')
]
