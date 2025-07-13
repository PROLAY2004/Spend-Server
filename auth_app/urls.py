from django.urls import path,include
from auth_app import views

urlpatterns = [
    path('Login/', views.signin, name='Login'),
    path("OTP/<str:userid>/", views.checkOTP, name='verification'),
    path("Logout/", views.signout, name='Logout'),
    path("Google/", views.google, name='GoogleAuth')
]
