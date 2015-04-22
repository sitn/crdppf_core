# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from crdppf.models import DBSession
from papyrus.protocol import Protocol
from crdppf.models import Property

@view_config(route_name='get_property', renderer='geojson')
def get_property(request):
    
    if 'ids' not in request.params:
        return HTTPBadRequest(detail='Please add a valid id in your request')

    ids = request.params['ids'].split(',')

    proto = Protocol(DBSession, Property, 'geom')

    filter ="idemai IN ("
    for id in ids:
        filter += "'" + id + "',"
    filter = filter[0:len(filter)-1] + ")"

    return proto.read(request, filter=filter)
