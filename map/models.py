# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib.gis.db import models

# Create your models here.

class Forty(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True,serialize=False,verbose_name='GID')
    nazwa = models.CharField(max_length=50)
    adres = models.CharField(max_length=50)
    typ = models.CharField(max_length=15)
    otwarty = models.CharField(max_length=2)
    zwiedzanie = models.CharField(max_length=2)
    mpoly = models.MultiPolygonField()
    objects = models.GeoManager()

    def __str__(self):
        return self.nazwa
