from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # LOGIN LOGOUT
    path('login/', auth_views.LoginView.as_view(
        template_name='auth/login.html'
    ), name='login'),

    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # DASHBOARD JADI HOME
    path('', include('dashboard.urls')),

    # APP LAIN
    path('helpdesk/', include('helpdesk.urls')),
    path('inventaris/', include('inventaris.urls')),
    path('gudang/', include('gudang.urls')),
    path('jaringan/', include('jaringan.urls')),
    path('pemeliharaan/', include('pemeliharaan.urls')),
    path('permintaan/', include('permintaan.urls')),
    path('setup/', include('setup.urls')),
    path('unit/', include('unit.urls')),
    path('pengadaan/', include('pengadaan.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
