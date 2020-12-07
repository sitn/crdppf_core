# -*- coding: UTF-8 -*-

from crdppf import db_config
from crdppf.extract import Extract
from crdppf.lib.wmts_parsing import wmts_layer
#from crdppf.lib.geometry_functions import get_feature_bbox, get_print_format, get_feature_center

from crdppf.util.get_feature_functions import get_features_function
from crdppf.util.documents import get_document_ref, get_documents
from crdppf.util.pdf_functions import get_feature_info, get_translations, get_print_format
from crdppf.models import DBSession
from crdppf.models.models import AppConfig

from geoalchemy2.shape import to_shape, WKTElement
import logging

log = logging.getLogger(__name__)


def get_mapbox(feature_center, scale, buffer, height, width, fitratio):
    """Function to calculate the coordinates of the map bounding box in the real world
        height: map height in mm
        width: map width in mm
        scale: the map scale denominator
        feature_center: center point (X/Y) of the real estate feature
    """

    scale = scale*buffer
    delta_Y = round((height*scale/1000)/2, 1)
    delta_X = round((width*scale/1000)/2, 1)
    X = round(feature_center[0], 1)
    Y = round(feature_center[1], 1)

    map_bbox = ''.join([
        'POLYGON((',
        str(X-delta_X)+' ',
        str(Y-delta_Y)+',',
        str(X-delta_X)+' ',
        str(Y+delta_Y)+',',
        str(X+delta_X)+' ',
        str(Y+delta_Y)+',',
        str(X+delta_X)+' ',
        str(Y-delta_Y)+',',
        str(X-delta_X)+' ',
        str(Y-delta_Y),
        '))'
    ])

    return map_bbox


def set_documents(topicid, doctype, docids, featureinfo, geofilter, doclist):
    """ Function to fetch the documents related to the restriction:
    legal provisions, temporary provisions, references
    """

    docs = []
    documents = []

    if geofilter is True:
        filters = {
            "docids": docids,
            "topicid": topicid,
            "cadastrenb": featureinfo["numcom"],
            "chmunicipalitynb": featureinfo["nufeco"]
        }
    else:
        filters = {"docids": docids}

    if len(docids) > 0:
        docs = get_documents(filters)
    else:
        docs = []

    # store the documents in a list
    if len(docs) > 0:
        doc = ""
        for doc in docs:
            if doc['officialnb'] is None:
                doc['officialnb'] = ""
            if doc['abbreviation'] is None:
                doc['abbreviation'] = ""
            if doc['title'] == '' or doc['title'] is None:
                doc['title'] = doc['officialtitle']
            if doc['doctype'] == doctype and doc['documentid'] in docids and doc['documentid'] not in doclist:
                documents.append({"documentid": doc['documentid'], "title": doc['title'], "officialtitle": doc['officialtitle'], "remoteurl": doc['remoteurl'], "abbreviation": doc['abbreviation'], "officialnb": doc['officialnb']})

            if doc['doctype'] == doctype and geofilter is True and doc['documentid'] not in docids:
                if doc['title'] == '' or doc['title'] is None:
                    doc['title'] = doc['officialtitle']
                documents.append({"documentid": doc['documentid'], "title": doc['title'], "officialtitle": doc['officialtitle'], "remoteurl": doc['remoteurl'], "abbreviation": doc['abbreviation'], "officialnb": doc['officialnb']})

    return documents


def get_legend_classes(bbox, layername, translations, srid):
    """ Collects all the features in the map perimeter into a list to create a dynamic legend
    """
    # transform coordinates from wkt to SpatialElement for intersection
    polygon = WKTElement(bbox.wkt, srid)
    mapfeatures = get_features_function(polygon, {'layerList': layername, 'translations': translations})
    if mapfeatures is not None:
        classes = []
        for mapfeature in mapfeatures:
            if mapfeature['properties'] is None:
                mapfeature['properties'] = '9999'
            if isinstance(mapfeature['properties'], int):
                mapfeature['properties'] = str(mapfeature['codegenre'])
            classes.append({"codegenre": str(mapfeature['properties']['codegenre']), "teneur": mapfeature['properties']['teneur']})

    return classes


def add_layer(layer, featureid, featureinfo, translations, appconfig, topicdata):

    layerlist = {}
    results = get_features_function(featureinfo['geom'], {'layerList': layer.layername, 'id': featureid, 'translations': translations})

    if results:
        layerlist[str(layer.layerid)] = {'layername': layer.layername, 'features': []}
        resultlist = set([])
        codegenres = set([])

        for result in results:
            codegenres.add(result['properties']['codegenre'])
            for property in ['geometry', 'type']:
                del result[property]
            for idx in ['theme', 'layerName']:
                del result['properties'][idx]
            resultlist.add(str(result['id']))
        groupedresult = {}
        for code in codegenres:
            for result in results:
                if result['properties']['intersectionMeasure'] == ' ':
                    measure = 1
                else:
                    measure = int(result['properties']['intersectionMeasure'].replace(' : ', '').replace(' - ', '').replace('[m2]', '').replace('[m]', ''))
                if result['properties']['codegenre'] == code:
                    if code in groupedresult:
                        groupedresult[code]["intersectionMeasure"] += measure
                    else:
                        groupedresult[code] = {
                            'teneur': result['properties']['teneur'],
                            'codegenre':result['properties']['codegenre'],
                            'statutjuridique': result['properties']['statutjuridique'],
                            'datepublication': result['properties']['datepublication'],
                            'geomType': result['properties']['geomType'],
                            "intersectionMeasure": measure
                            }
            layerlist[str(layer.layerid)]['features'].append(groupedresult[code])
        layerlist[str(layer.layerid)]['ids'] = resultlist
    else:
        layerlist = None

    return layerlist


def get_content(id, request):
    """ TODO....
        Explain how the whole thing works...
    """
    # Start a session
    session = request.session
    configs = DBSession.query(AppConfig).all()

    # initalize extract object
    extract = Extract(request)
    directprint = False
    if extract.reporttype == 'file':
        extract.reporttype = 'reduced'
        directprint = True
    else:
        reporttype = extract.reporttype

    for config in configs:
        if config.parameter not in ['crdppflogopath', 'cantonlogopath']:
            extract.baseconfig[config.parameter] = config.paramvalue

    extract.topiclegenddir = request.static_url('crdppfportal:static/public/legend/')

    # for simplification
    translations = extract.translations

    # 1) If the ID of the parcel is set get the basic attributs of the property
    # else get the ID (id) of the selected parcel first using X/Y coordinates of the center
    # ---------------------------------------------------------------------------------------------------
    featureinfo = extract.real_estate  # '1_14127' # test parcel or '1_11340'

    # 3) Get the list of all the restrictions by topicorder set in a column
    # ------------------------------------------
    topics = extract.topics
    restrictions = extract.restrictions

    # Configure the WMTS background layer

    defaultTiles = request.registry.settings['defaultTiles']
    wmts = {
        'url': request.registry.settings['wmts_getcapabilities_url'],
        'defaultTiles': defaultTiles,
        'layer': defaultTiles['wmtsname']
    }

    wmts_layer_ = wmts_layer(wmts['url'], wmts['layer'])
    extract.baseconfig['wmts'] = wmts

    wms_base_layers = request.registry.settings['app_config']['crdppf_wms_layers']
    map_buffer = request.registry.settings['app_config']['map_buffer']
    basemaplayers = {
        "baseURL": request.registry.settings['crdppf_wms'],
        "opacity": 1,
        "type": "WMS",
        "layers": wms_base_layers,
        "imageFormat": "image/png",
        "styles": "default",
        "customParams": {
            "TRANSPARENT": "true"
        }
    }

    municipality = featureinfo['nomcom'].strip()
    cadastre = featureinfo['nomcad'].strip()
    propertynumber = featureinfo['nummai'].strip()
    propertytype = featureinfo['type'].strip()
    propertyarea = featureinfo['area']
    report_title = translations[str(extract.reporttype+'extracttitlelabel')]

    # AS does the german language, the french contains a few accents we have to replace to fetch the banner which has no accents in its pathname...
    conversion = [
        [u'â', 'a'],
        [u'ä', 'a'],
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
        [u'-', '_'],
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

    legenddir = '/'.join([
        request.registry.settings['localhost_url'],
        'proj/images/icons/'])

    # Get the raw feature BBOX
    #extract.basemap['bbox'] = get_feature_bbox(id)
    #bbox = extract.basemap['bbox']
    bbox = extract.real_estate['BBOX']

    if bbox is False:
        log.warning('Found more then one bbox for id: %s' % id)
        return False

    # Get the feature center
    #extract.basemap['feature_center'] = get_feature_center(id)
    #feature_center = extract.basemap['feature_center']
    feature_center = [extract.real_estate['centerX'], extract.real_estate['centerY']]

    if feature_center is False:
        log.warning('Found more then one geometry for id: %s' % id)
        return False

    # Get the print BOX
    print_box = get_print_format(bbox, request.registry.settings['pdf_config']['fitratio'])
    map_bbox = get_mapbox(feature_center, print_box['scale'], map_buffer, print_box['height'], print_box['width'],
                          request.registry.settings['pdf_config']['fitratio'])

    log.warning('Calling feature: %s' % request.route_url('get_property')+'?id='+id)

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

    basemap = {
        "projection": "EPSG:"+str(extract.srid),
        "dpi": 150,
        "rotation": 0,
        "center": feature_center,
        "scale": print_box['scale']*map_buffer,
        "longitudeFirst": "true",
        "layers": [{
            "type": "geojson",
            "geoJson": request.route_url('get_property')+'?id='+id,
            "style": {
                "version": "2",
                "strokeColor": "gray",
                "strokeLinecap": "round",
                "strokeOpacity": 0.5,
                "[INTERSECTS(geometry, "+wkt_polygon+")]": {
                    "symbolizers": [{
                        "strokeColor": "red",
                        "strokeWidth": 4,
                        "type": "line"
                    }]
                }
            }
        }, wmts_layer_
        ]
    }

    data = []
    topicdata = {}
    topicdata["doclist"] = []
    appconfig = extract.baseconfig
    concernedtopics = []
    notconcernedtopics = []
    emptytopics = []

    for topic in topics:
        #log.warning('Parsing topic : %s' % topic.topicid)

        currenttopic = extract.topiclist[topic.topicorder]
        if currenttopic['legalprovisions'] == []:
            currenttopic['legalprovisions'] = [{
                'officialtitle': "",
                'title': "",
                'officialnb': "",
                'abbreviation': "",
                'remoteurl': ""
            }]
        if currenttopic['hints'] == []:
            currenttopic['hints'] = [{
                        "title": "",
                        "officialtitle": "",
                        "officialnb": "",
                        "abbreviation": "",
                        "remoteurl": ""
                    }]
        if currenttopic['bboxlegend'] == []:
            currenttopic['bboxlegend'] = [{
                        "codegenre": "",
                        "teneur": ""
                    }]

        if currenttopic['categorie'] == 3:
            data.append({
                "topicname": currenttopic['topicname'],
                "map":  currenttopic['map'],
                "restrictions":  currenttopic['restrictions'],
                "bboxlegend":  currenttopic['bboxlegend'],
                "completelegend":  currenttopic['topiclegend'],
                "legalbases":  currenttopic['legalbases'],
                "legalprovisions":  currenttopic['legalprovisions'],
                "references":  currenttopic['hints'],
                "authority": [
                     currenttopic['authority']
                ]
            })
        elif currenttopic['categorie'] == 1:
            notconcernedtopics.append(
                currenttopic['topicname']
            )
        else:
            emptytopics.append(
                currenttopic['topicname']
            )

    d = {
        "attributes": {
            "reporttype": extract.reporttype,
            "directprint": directprint,
            "extractcreationdate": extract.creationdate,
            "filename": extract.filename,
            "extractid": extract.id,
            "map": basemap,
            "municipality": municipality,
            "cadastre": cadastre,
            "cadastrelabel": "Cadastre",
            "propertytype": extract.real_estate['type'],
            "propertynumber": propertynumber,
            "EGRIDnumber": featureinfo['egrid'],
            "municipalitylogopath": municipalitylogopath,
            "federalmunicipalitynumber": featureinfo['nufeco'],
            "competentauthority": extract.baseconfig['competentauthority'],
            "titlepage": [{
                "title": report_title,
                "certificationinstance": "",
                "certificationtext": "",
            }],
            "concernedtopics":  concernedtopics,
            "notconcernedtopics": ";".join(notconcernedtopics),
            "emptytopics": ";".join(emptytopics),
            "propertyarea": propertyarea,
            "datasource": data
        },
        "layout": "report",
        "outputFilename": extract.filename,
        "outputFormat": "pdf"
    }

    # pretty printed json data for the extract
    #import json
    #jsonfile = open('C:/Temp/'+extract.filename+'.json', 'w')
    #jsondata = json.dumps(d, indent=4)
    #jsonfile.write(jsondata)
    #jsonfile.close()

    return d
