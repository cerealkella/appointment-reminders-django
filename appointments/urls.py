from django.conf.urls import include
from django.conf.urls import re_path
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

urlpatterns = [
    re_path(r'^$',
            TemplateView.as_view(template_name='index.html'),
            name='home'),
    re_path(r'^appointments/', include('reminders.urls')),

    # Include the Django admin
    re_path(r'^admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
]

import schedulers.jobs  # NOQA @isort:skip
import logging
logging.basicConfig(level="DEBUG")
