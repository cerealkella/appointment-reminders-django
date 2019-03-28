from django.conf.urls import include
from django.conf.urls import re_path
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    re_path(r'^$',
            TemplateView.as_view(template_name='index.html'),
            name='home'),
    re_path(r'^appointments/', include('reminders.urls')),

    # Include the Django admin
    re_path(r'^admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# Only run if Dramatiq is set to Autostart
if settings.SCHEDULER_AUTOSTART:
    import schedulers.jobs
    print("Starting Scheduler from urls.py")
import logging
logging.basicConfig(level="DEBUG")
