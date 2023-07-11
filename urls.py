from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import TemplateView

urlpatterns = [
    path('upload/', include('upload.urls')),
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='main_index.html'), name='main_index')
]
