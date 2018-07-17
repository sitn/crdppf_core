# -*- coding: utf-8 -*-

from pyramid.httpexceptions import HTTPBadRequest
from pyramid.view import view_config

from crdppf.models import DBSession
from papyrus.protocol import Protocol
from crdppf.models import Property


@view_config(route_name='get_property', renderer='geojson')
def get_property(request):

    if 'id' not in request.params:
        return HTTPBadRequest(detail='Please add a valid id in your request')

    id_ = request.params['id']

    proto = Protocol(DBSession, Property, 'geom')

    id_ = DBSession.query(Property.noobj).filter(Property.id==id_).first()

    if id_ is None:
        return HTTPBadRequest(detail='No object has been found for this id')

    return proto.read(request, id=id_)
