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
                d[str(tile.baselayer)] = {
                    'tile_date':tile.baselayer+u'_'+tile.tile_date,
                    'tile_format': tile.tile_format
                    }
        else:
            d['plan_cadastral'] = {
                'tile_date':'plan_cadastral_c2c',
                'tile_format':'image/png'}
            d['plan_ville'] = {'tile_date':'plan_ville_c2c',
                'tile_format':'image/png'}
    #~ except:
        #~ pass

        return d
