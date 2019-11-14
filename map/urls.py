from django.conf.urls import url, include
from . import views
from rest_framework.urlpatterns import format_suffix_patterns


app_name = 'map'
urlpatterns = [
    url(r'^$', views.index, name = 'index'),
    url(r'^directions/(?P<start_coord>[- ]?\d+\.?\d+,\d+\.\d+)&(?P<end_coord>[- ]?\d+\.?\d+,\d+\.\d+)$',
    views.create_route, name = 'directions'),
]

urlpatterns = format_suffix_patterns(urlpatterns)

'''
urlpatterns = patterns('maps.views',
# ex valid call from to /api/directions/1587848.414,5879564.080,2&1588005.547,5879736.039,2
url(r'^(?P<map_name>\w+)/$', 'route_map', name='route-map'),
)'''
