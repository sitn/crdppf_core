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

    #~ try:
        from crdppfportal.models import Tiles
        tiles = DBSession.query(Tiles).all()
        if len(tiles) > 0:
            for tile in tiles:
                tilesconfig.append({str(tile.baselayer): tile.tile_date})
        else:
            d['plan_cadastral'] = 'plan_cadastral_c2c'
            d['plan_ville'] = 'plan_ville_c2c'
    #~ except:
        #~ pass

        return d
