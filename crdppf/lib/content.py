# -*- coding: UTF-8 -*-

from copy import deepcopy
import ast
from datetime import datetime

from crdppf.lib.wmts_parsing import wmts_layer
from crdppf.lib.geometry_functions import get_feature_bbox, get_print_format, get_feature_center

from crdppf.util.pdf_functions import get_feature_info, get_translations

import logging

log = logging.getLogger(__name__)

def get_content(idemai, request):
    """ TODO....
        Explain how the whole thing works...
    """
    # Start a session
    session = request.session
    
    # Define language to get multilingual labels for the selected language
    # defaults to 'fr': french - this may be changed in the appconfig
    if 'lang' not in session:
        lang = request.registry.settings['default_language'].lower()
    else : 
        lang = session['lang'].lower()
    translations = get_translations(lang)
    
    extractcreationdate = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Configure the WMTS background layer
    url = request.registry.settings['wmts_getcapabilities_url']
    defaultTiles =  ast.literal_eval("{"+request.registry.settings['defaultTiles']+"}")
    layer = defaultTiles['wmtsname']
    wmts_layer_ = wmts_layer(url, layer)

    featureInfo = get_feature_info(idemai, translations)
    municipality = featureInfo['nomcom'].strip()
    cadastre = featureInfo['nomcad'].strip()
    propertynumber = featureInfo['nummai'].strip()
    type = featureInfo['type'].strip()
    propertyarea = featureInfo['area']
    report_title = translations['reducedcertifiedextracttitlelabel']
    certificationlabel = translations['certificationlabel']
    
    # AS does the german language, the french contains a few accents we have to replace to fetch the banner which has no accents in its pathname...
    conversion = [
        [u'â', 'a'],
        [u'ä' ,'a'],
        [u'à', 'a'],
        [u'ô', 'o'],
        [u'ö', 'o'],
        [u'ò', 'o'],
        [u'û', 'u'],
        [u'ü', 'u'],
        [u'ù', 'u'],
        [u'î', 'i'],
        [u'ï', 'i'],
        [u'ì', 'i'],
        [u'ê', 'e'],
        [u'ë', 'e'],
        [u'è', 'e'],
        [u'é', 'e'],
        [u' ', ''],
        [u'-','_'],
        [u'(NE)', ''],
        [u' (NE)', '']
    ]

    municipality_escaped = municipality.strip()

    for char in conversion:
        municipality_escaped = municipality_escaped.replace(char[0], char[1])
        
    municipalitylogodir = '/'.join([
        request.registry.settings['localhost_url'],
        'proj/images/ecussons/'])
    municipalitylogopath = municipalitylogodir + municipality_escaped + '.png'

    # Get the raw feature BBOX
    bbox = get_feature_bbox(idemai)

    if bbox is False:
        log.warning('Found more then one bbox for idemai: %s' % idemai)
        return False

    # Get the feature center
    feature_center = get_feature_center(idemai)

    if feature_center is False:
        log.warning('Found more then one geometry for idemai: %s' % idemai)
        return False

    # Get the print BOX
    print_box = get_print_format(bbox, request.registry.settings['pdf_config']['fitratio'])

    log.warning('Calling feature: %s' % request.route_url('get_property')+'?id='+idemai)

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
            "geoJson": request.route_url('get_property')+'?id='+idemai,
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

    data = [
        {
          "topic_title": "bli",
          "topic_text": "bla",
          "map": map
          },
        {
          "topic_title": "blu",
          "topic_text": "blo",
          "map": map
          }
        ]
    
    d = {
    #    "datasource": [],
        "map": map
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
        "attributes": {
        "extractcreationdate": extractcreationdate,
        "map": map,
        "municipality": municipality,
        "cadastre": cadastre,
        "propertytype": type,
        "propertynumber": propertynumber,
        "EGRIDnumber": featureInfo['no_egrid'],
        "municipalitylogopath": municipalitylogopath,
        "federalmunicipalitynumber": featureInfo['nufeco'],
        "competentauthority": 'Placeholder',
        "report_title": report_title,
        "propertyarea": propertyarea,
        "datasource": data
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
    #~ sdf
    return d
