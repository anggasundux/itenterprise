from django.urls import path
from . import views

urlpatterns = [
    path('', views.unit_list, name='unit_list'),
    path('add/', views.unit_add, name='unit_add'),
    path('edit/<int:id>/', views.unit_edit, name='unit_edit'),
    path('delete/<int:id>/', views.unit_delete, name='unit_delete'),
    path('export/', views.export_unit_excel, name='unit_export_excel'),

]
