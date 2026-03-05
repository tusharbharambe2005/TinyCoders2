"""
Users app URL routes.
"""
from django.urls import path
from .views import RegisterUserView, AddTrustedContactView, GetUserView, GetOrCreateUserByPhoneView

urlpatterns = [
    path("register", RegisterUserView.as_view(), name="user-register"),
    path("get-or-create", GetOrCreateUserByPhoneView.as_view(), name="get-or-create-user"),
    path("trusted-contact", AddTrustedContactView.as_view(), name="add-trusted-contact"),
    path("<uuid:user_id>", GetUserView.as_view(), name="get-user"),
]
