# -*- coding: utf-8 -*-

from pyramid.view import view_config

from crdppf.models import DBSession

class Entry(object):
    
    def __init__(self, request):
        self.debug = "debug" in request.params
        self.settings = request.registry.settings
        self.request = request
        
    @view_config(route_name='home', renderer = 'crdppf:templates/derived/crdppf.mako')
    def home(self):

        d = {
            'debug': self.debug
            }

        return d
