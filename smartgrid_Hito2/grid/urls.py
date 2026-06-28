from django.urls import path
from . import views

urlpatterns = [
    path('',              views.landing_view,      name='landing'),
    path('app/',          views.app_view,          name='app'),
    path('api/red/',      views.api_red,      name='api_red'),
    path('api/exportar/', views.api_exportar, name='api_exportar'),
]
