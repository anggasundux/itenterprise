from django.contrib import admin
from .models import PerangkatJaringan, VLAN, PortSwitch

admin.site.register(PerangkatJaringan)
admin.site.register(VLAN)
admin.site.register(PortSwitch)
