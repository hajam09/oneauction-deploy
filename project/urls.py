from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import HttpResponse

def health(request):
    return HttpResponse('health')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mainapp.urls')),
    path('health/', health, name="health"),
]
