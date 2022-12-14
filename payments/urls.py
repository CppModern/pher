from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path("verifadd/", views.addverification),
    path("verif/<pk>/", views.getverificatondata),
]

