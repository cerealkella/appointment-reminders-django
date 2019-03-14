from django.conf.urls import re_path
from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import (
    AppointmentCreateView,
    AppointmentDeleteView,
    AppointmentDetailView,
    AppointmentListView,
    AppointmentUpdateView,
)

urlpatterns = [
    # List and detail views
    path('appointments/', login_required(AppointmentListView.as_view(template_name="login_form.html")), name='list_appointments'),
    #re_path(r'^$', AppointmentListView.as_view(), name='list_appointments'),
    re_path(r'^(?P<pk>[0-9]+)$', login_required(
            AppointmentDetailView.as_view()),
            name='view_appointment'),

    # Create, update, delete
    re_path(r'^new$', login_required(AppointmentCreateView.as_view()), name='new_appointment'),
    re_path(r'^(?P<pk>[0-9]+)/edit$',
            login_required(AppointmentUpdateView.as_view()),
            name='edit_appointment'),
    re_path(r'^(?P<pk>[0-9]+)/delete$',
            login_required(AppointmentDeleteView.as_view()),
            name='delete_appointment'),
]
