from django.urls import path
from . import views

urlpatterns = [
    path('', views.setup_dashboard, name='setup_dashboard'),
    
    path('users/', views.user_list, name='user_list'),
    path('users/add/', views.user_add, name='user_add'),
    path('users/edit/<int:id>/', views.user_edit, name='user_edit'),
    path('users/delete/<int:id>/', views.user_delete, name='user_delete'),
]
