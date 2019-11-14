# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import traceback
from django.shortcuts import render_to_response
from map.models import Forty
from django.http import HttpResponse, HttpResponseNotFound
from vectorformats.Formats import Django, GeoJSON
from rest_framework.decorators import api_view
from rest_framework.response import Response
from geojson import loads, Feature, FeatureCollection
import logging
from django.db import connection

logger = logging.getLogger(__name__)

# Create your views here.

def index(request):
    Forty_objects = Forty.objects.all()
    return render_to_response("map/home.html", {'Forts' : Forty})

def get_geojson(request):
    defzwiedzanie=request.GET['zwiedzanie']
    deftype=request.GET['typ']

    forty_ob = Forty.objects.filter(typ__contains=deftype, zwiedzanie__contains=defzwiedzanie)

    djf = Django.Django(geodjango='mpoly',properties=['nazwa','adres','typ','otwarty','zwiedzanie'])
    geoj = GeoJSON.GeoJSON()
    gjson = geoj.encode(djf.decode(forty_ob))

    return HttpResponse(gjson)

def find_closest_network_node(x_coord,y_coord):
    logger.debug("now running function find_closest_network_node")
    cur = connection.cursor()

    #find nearest node in range of 500m and snap to it
    query = """ SELECT
        verts.id as id
        FROM public.cycleways_100_noded_vertices_pgr as verts
        INNER JOIN
            (select ST_PointFromText('POINT(%s %s)', 4326) as geom) AS pt
        ON ST_DWithin(verts.the_geom, pt.geom, 500.0)
        ORDER BY ST_3DDistance(verts.the_geom, pt.geom)
        LIMIT 1;"""

    cur.execute(query, (x_coord, y_coord))
    query_result = cur.fetchone()
    #check if result is not empty
    if query_result is not None:
        point_on_networkline = int (query_result[0])
        return point_on_networkline
    else:
        logger.debug("query is none, maybe range is too small")
        return False

@api_view (['GET','POST'])
def create_route (request, start_coord, end_coord):
    if request.method == 'GET' or request.method == 'POST':
        cur = connection.cursor()
        x_start_coord = float(start_coord.split(',')[0])
        y_start_coord = float(start_coord.split(',')[1])

        x_end_coord = float(end_coord.split(',')[0])
        y_end_coord = float(end_coord.split(',')[1])

        start_node_id = find_closest_network_node(x_start_coord, y_start_coord)
        end_node_id = find_closest_network_node(x_end_coord, y_end_coord)

        routing_query ="SELECT seq, id1 as node, id2 as edge, cost, ST_AsGeoJSON(geom) AS geoj FROM pgr_dijkstra('SELECT id, source, target, st_length(geom) as cost FROM public.cycleways_100_noded', %s, %s, FALSE, FALSE) AS dij_route JOIN public.cycleways_100_noded AS input_network ON dij_route.id2 = input_network.id;"

        if start_node_id or end_node_id:
            cur.execute(routing_query, (start_node_id, end_node_id))
        else:
            logger.error("start or end node is None " + str(start_node_id))
            return HttpResponseNotFound ('<h1> Sorry, no start or end node found within 500m</h1>')

        route_segments = cur.fetchall()
        route_result = []

        for segment in route_segments:
            seg_cost = segment[3]
            geojs = segment[4]
            geojs_geom = loads(geojs)
            geojs_feat = Feature(geometry=geojs_geom, properties={
            'length': seg_cost
            })
            route_result.append(geojs_feat)

        geojs_fc = FeatureCollection(route_result)

        try:
            return Response(geojs_fc)
        except:
            logger.error("error exporting to json model: " + str(geojs_fc))
            logger.error(traceback.format_exc())
            return Response ({'error': 'either no JSON or no key params in your JSON'})
    else:
        return HttpResponseNotFound('<h1> Sorry not a GET or POST request</h1>')
