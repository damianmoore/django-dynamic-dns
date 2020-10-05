from django.urls import include, path, re_path
from django.contrib import admin


admin.autodiscover()

urlpatterns = [
    path('dynamicdns/', include('dynamicdns.urls')),
    path('admin/', admin.site.urls),
]
