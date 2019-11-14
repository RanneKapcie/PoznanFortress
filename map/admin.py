# -*- coding: utf-8 -*-

from django.contrib.gis import admin
from .models import Forty

# Register your models here.
admin.site.register(Forty, admin.GeoModelAdmin)
