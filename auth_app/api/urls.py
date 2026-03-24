from django.urls import path
from .views import (
    RegisterView, ActivateAccountView,
    LoginView, LogoutView,
    CookieTokenRefreshView,
    PasswordResetRequestView, PasswordResetConfirmView,
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<str:uidb64>/<str:token>/',
         ActivateAccountView.as_view(), name='activate'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', PasswordResetRequestView.as_view(),
         name='password-reset'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/',
         PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
