from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('autentificacion/', include('autentificacion.urls')),
    path('conciliacion/', include('conciliacion.urls')),
    # path('reportes/', include('reportes.urls')),
    # path('gestion/', include('admin_app.urls')), esto despues se agrega

    # Ruta por defecto redirige a autenticación
    path('', include('autentificacion.urls')),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)