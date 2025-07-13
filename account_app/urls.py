from django.urls import path,include
from account_app import views

urlpatterns = [
    path('Home/<str:userid>/', views.dashboard, name='Dashboard'),
    path('Insert/Data/<str:userid>/', views.insert, name='Add_Record'),
    path('View/Data/<str:userid>/', views.view, name='View_Record'),
    path('Filter/Data/<str:userid>/', views.search, name='Filter_Record'),
    path('Modify/Data/<str:userid>/', views.modify, name='Modify_Record'),
    path('Settings/<str:userid>/', views.setting, name='Settings'),
    path('Support/<str:userid>/', views.support, name='Support'),
    path('Support/Ticket/<str:userid>/', views.ticket, name='Support_Ticket'),
    path('Support/Ticket/Admin/<str:userid>/', views.admin, name='Support_Admin'),
    path('Support/Ticket/<str:ticketid>/<str:userid>/', views.chat, name='Support_chat'),
    path('Support/Ticket/Admin/<str:ticketid>/<str:userid>/', views.adminChat, name='Admin_chat'),
    path('Delete/Data/<str:recordid>/<str:userid>/', views.delRecord, name='Delete_Record'),
    path('Delete/User/<str:userid>/', views.deluser, name='Delete_Account'),
    path('Edit/Data/<str:recordid>/<str:userid>/', views.edit, name='Edit_Record'),
]
