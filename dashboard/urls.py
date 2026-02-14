from django.urls import path
from .views import dashboard_home, realtime_status

urlpatterns = [
    path('', dashboard_home, name='dashboard'),
    path('realtime/', realtime_status, name='realtime_status'),
]
