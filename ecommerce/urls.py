"""
URL configuration for ecommerce project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('api.urls'))
] 

#SOLO DESARROLLO - Automático y seguro de carga de archivos
#Es decir que si estamos en modo desarrollo entonces se cargan los archivos estaticos
if settings.DEBUG: #← ¡ES SEGURIDAD! No lo quites nunca 
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0]) # Configuracion de archivos estaticos (carga de archivos css y js)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # Configuracion de las imagenes, Aqui se cargan las imagenes
