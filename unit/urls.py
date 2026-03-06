from django.urls import path
from . import views

urlpatterns = [

    # ================= UNIT =================
    path('', views.unit_list, name='unit_list'),
    path('add/', views.unit_add, name='unit_add'),
    path('edit/<int:id>/', views.unit_edit, name='unit_edit'),
    path('delete/<int:id>/', views.unit_delete, name='unit_delete'),

    # ⭐ DETAIL UNIT (yang bikin error kemarin)
    path('detail/<int:id>/', views.unit_detail, name='unit_detail'),

    # ⭐ EXPORT
    path('export/', views.export_unit_excel, name='export_unit_excel'),

    # ================= PERANGKAT TAMBAHAN =================
    path('perangkat/add/<int:unit_id>/', views.perangkat_add, name='perangkat_add'),
    path('perangkat/delete/<int:id>/', views.perangkat_delete, name='perangkat_delete'),
]
