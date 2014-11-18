# -*- coding: UTF-8 -*-
from pyramid.view import view_config

from crdppf.models import DBSession, Translations

class Config(object):
    def __init__(self, request):
        self.debug = "debug" in request.params
        self.settings = request.registry.settings
        self.request = request
        
    @view_config(route_name='configpanel', renderer = 'crdppf:templates/derived/configpanel.mako')
    def configpanel(self):
        d = {
            'debug': self.debug
        }
        return d

    @view_config(route_name='formulaire_reglements',renderer = 'crdppf:templates/derived/formulaire_reglements.mako')
    def formulaire_reglements(self):
        d = {
            'debug': self.debug
        }
        return d