from django.urls import path
from .views import pemeliharaan_list

urlpatterns = [
    path('', pemeliharaan_list, name='pemeliharaan_list'),
]
