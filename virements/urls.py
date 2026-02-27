from django.urls import path
from . import views

app_name = 'virements'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('initiation/', views.initiation_virement, name='initiation'),
    path('initiation/success/<uuid:virement_id>/', views.initiation_success, name='initiation_success'),
    path('rejet/<uuid:virement_id>/', views.rejet_virement, name='rejet'),
    path('rejet/success/<uuid:virement_id>/', views.rejet_success, name='rejet_success'),
    path('historique/', views.historique, name='historique'),
    path('profil/', views.profil_utilisateur, name='profil'),
    path('download-pdf/<uuid:virement_id>/', views.download_pdf, name='download_pdf'),
]