"""
Users app URL routes.
"""
from django.urls import path
from .views import RegisterUserView, AddTrustedContactView, GetUserView

urlpatterns = [
    path("register", RegisterUserView.as_view(), name="user-register"),
    path("trusted-contact", AddTrustedContactView.as_view(), name="add-trusted-contact"),
    path("<uuid:user_id>", GetUserView.as_view(), name="get-user"),
]
