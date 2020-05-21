from django.urls import include, path

from .views import dynamic_dns_read, dynamic_dns_update


urlpatterns = [
    path('read/<str:domain>/', dynamic_dns_read),
    path('update/<str:domain>/', dynamic_dns_update),
]
