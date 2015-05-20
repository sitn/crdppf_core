# -*- coding: UTF-8 -*-

from copy import deepcopy
import ast

from crdppf.lib.wmts_parsing import wmts_layer
from crdppf.lib.geometry_functions import get_feature_bbox, get_print_format, get_feature_center


import logging

log = logging.getLogger(__name__)

def get_content(idemai, request):
    """ TODO....
        Explain how the whole thing works...
    """

    # Configure the WMTS background layer
    url = request.registry.settings['wmts_getcapabilities_url']
    defaultTiles =  ast.literal_eval("{"+request.registry.settings['defaultTiles']+"}")
    layer = defaultTiles['wmtsname']
    wmts_layer_ = wmts_layer(url, layer)

    # Get the raw feature BBOX
    bbox = get_feature_bbox(idemai)

    # Get the feature center
    feature_center = get_feature_center(idemai)

    # Get the print BOX
    print_box = get_print_format(bbox, request.registry.settings['pdf_config']['fitratio'])

    log.warning('Calling feature: %s' % request.route_url('get_property')+'?ids='+idemai)

    wkt_polygon = ''.join([
        'POLYGON((',
        str(bbox['minX'])+' ',
        str(bbox['minY'])+',',
        str(bbox['minX'])+' ',
        str(bbox['maxY'])+',',
        str(bbox['maxX'])+' ',
        str(bbox['maxY'])+',',
        str(bbox['maxX'])+' ',
        str(bbox['minY'])+',',
        str(bbox['minX'])+' ',
        str(bbox['minY']),
        '))'
    ])

    # This define the "general" map that we are going to copy x times,
    # one time as base map and x times as topic map.
    map = {
        "projection": "EPSG:21781",
        "dpi": 150,
        "rotation": 0,
        "center": feature_center,
        "scale": print_box['scale'],
        "longitudeFirst": "true",
        "layers": [{
            "type": "geojson",
            "geoJson": request.route_url('get_property')+'?ids='+idemai,
            "style": {
                "version": "2",
                "strokeColor": "gray",
                "strokeLinecap": "round",
                "strokeOpacity": 0.6,
                "[INTERSECTS(geometry, "+wkt_polygon+")]": {
                    "symbolizers": [{
                        "strokeColor": "green",
                        "strokeWidth": 2,
                        "type": "line"
                    }]
                }
            }
        }, wmts_layer_
        ]
    }

    #~ base_map = deepcopy(map)
    #~ base_map["bbox"] = " "

    d = {
    #    "datasource": [],
        "map": map,
     #   "base_map": base_map,
    }

    #~ maps = []


    #~ for map__ in maps:
        #~ my_map = deepcopy(map)
        #~ my_map["layers"][1]["layers"] = 'toto'
        #~ d["datasource"].push({
            #~ "map": my_map,
            #~ "legend_url": "http://...&style=toto.xml"
        #~ })

    d= {
        "attributes": {"map": map
        #~ "attributes": {"map": {
            #~ "bbox": [555932, 201899, 556079, 202001],
            #~ "dpi": 72,
            #~ "layers": [{
                #~ "type": "geojson",
                #~ "geoJson":"http://localhost:6544/property/get?ids=13_5199"
            #~ }],
            #~ "longitudeFirst": True,
            #~ "projection": "EPSG:21781",
            #~ "scale": 1000
        #~ }
        },
        "layout": "report"
    }

    return d
