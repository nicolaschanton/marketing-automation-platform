from django.urls import path
from please_marketing_growth_hack import views, views_signup_neighborhood


urlpatterns = [
    path('inscription', views.sign_up, name='sign_up'),
    path('inscription_ville', views_signup_neighborhood.sign_up, name='sign_up_ville'),
    path('merci', views.thanks, name='thanks'),
    path('merci_ville', views_signup_neighborhood.thanks, name='thanks_ville'),
    path('formulaire_invalide', views.invalid_form, name='formulaire_invalide'),
    path('formulaire_invalide_ville', views_signup_neighborhood.invalid_form, name='formulaire_invalide_ville'),
    path('404', views.error, name='404'),
    path('jeu_concours', views.game, name='jeu_concours'),
    path('jeu_concours_vernon', views.game_vernon, name='jeu_concours_vernon'),
    path('merci_vernon', views.game_vernon_merci, name='jeu_concours_merci_vernon')
]
