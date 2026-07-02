from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from usuarios.views import RootAPIView, StatusAPIView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', RootAPIView.as_view(), name='api-root'),
    path('api/status/', StatusAPIView.as_view(), name='api-status'),
    path('api/', include('usuarios.urls')),
    path('api/', include('rifas.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
