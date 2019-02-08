# -*- coding: UTF-8 -*-

from crdppf import db_config
from crdppf.extract import Extract
from crdppf.lib.wmts_parsing import wmts_layer
from crdppf.lib.geometry_functions import get_feature_bbox, get_print_format, get_feature_center

from crdppf.util.get_feature_functions import get_features_function
from crdppf.util.documents import get_document_ref, get_documents
from crdppf.util.pdf_functions import get_feature_info, get_translations

from crdppf.models import DBSession, Topics, AppConfig

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
            if doc['title'] == '' or doc['title'] is None:
                doc['title'] = doc['officialtitle']
            if doc['doctype'] == doctype and doc['documentid'] in docids and doc['documentid'] not in doclist:
                documents.append({"documentid": doc['documentid'], "officialtitle": doc['officialtitle'], "title": doc['title'], "remoteurl": doc['remoteurl']})

            if doc['doctype'] == doctype and geofilter is True and doc['documentid'] not in docids:
                if doc['title'] == '' or doc['title'] is None:
                    doc['title'] = doc['officialtitle']
                documents.append({"documentid": doc['documentid'], "officialtitle": doc['officialtitle'], "title": doc['title'], "remoteurl": doc['remoteurl']})

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
    results = get_features_function(featureinfo['geom'], {'layerList': layer.layername, 'id': featureid, 'translations': appconfig['translations']})

    if results:
        layerlist[str(layer.layerid)] = {'layername': layer.layername, 'features': []}
        resultlist = set([])
        for result in results:
            for property in ['geometry', 'type']:
                del result[property]
            for idx in ['theme', 'layerName']:
                del result['properties'][idx]
            resultlist.add(str(result['id']))
            layerlist[str(layer.layerid)]['features'].append(result['properties'])
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
    type = request.matchdict.get("type_")
    directprint = False
    if type == 'file':
        type = 'reduced'
        directprint = True
    for config in configs:
        if config.parameter not in ['crdppflogopath', 'cantonlogopath']:
            extract.baseconfig[config.parameter] = config.paramvalue
    extract.srid = db_config['srid']

    extract.topiclegenddir = request.static_url('crdppfportal:static/public/legend/')

    # Define language to get multilingual labels for the selected language
    # defaults to 'fr': french - this may be changed in the appconfig
    if 'lang' not in session:
        extract.baseconfig['lang'] = request.registry.settings['default_language'].lower()
    else:
        extract.baseconfig['lang'] = session['lang'].lower()
    extract.baseconfig['translations'] = get_translations(extract.baseconfig['lang'])
    # for simplification
    translations = extract.baseconfig['translations']

    # 1) If the ID of the parcel is set get the basic attributs of the property
    # else get the ID (id) of the selected parcel first using X/Y coordinates of the center
    # ---------------------------------------------------------------------------------------------------
    featureinfo = get_feature_info(id, extract.srid, translations)  # '1_14127' # test parcel or '1_11340'
    extract.filename = extract.id + featureinfo['featureid']

    # 3) Get the list of all the restrictions by topicorder set in a column
    # ------------------------------------------
    extract.topics = DBSession.query(Topics).order_by(Topics.topicorder).all()

    # Configure the WMTS background layer

    defaultTiles = request.registry.settings['defaultTiles']
    wmts = {
        'url': request.registry.settings['wmts_getcapabilities_url'],
        'defaultTiles': defaultTiles,
        'layer': defaultTiles['wmtsname']
    }

    wmts_layer_ = wmts_layer(wmts['url'], wmts['layer'])
    extract.baseconfig['wmts'] = wmts

    base_wms_layers = request.registry.settings['app_config']['crdppf_wms_layers']
    map_buffer = request.registry.settings['app_config']['map_buffer']
    basemaplayers = {
        "baseURL": request.registry.settings['crdppf_wms'],
        "opacity": 1,
        "type": "WMS",
        "layers": base_wms_layers,
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
    report_title = translations[str(type+'extracttitlelabel')]

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
    extract.header['municipality_escaped'] = municipality_escaped

    municipalitylogodir = '/'.join([
        request.registry.settings['localhost_url'],
        'proj/images/ecussons/'])
    municipalitylogopath = municipalitylogodir + municipality_escaped + '.png'
    extract.header['municipalitylogopath'] = municipalitylogopath
    legenddir = '/'.join([
        request.registry.settings['localhost_url'],
        'proj/images/icons/'])

    # Get the raw feature BBOX
    extract.basemap['bbox'] = get_feature_bbox(id)
    bbox = extract.basemap['bbox']

    if bbox is False:
        log.warning('Found more then one bbox for id: %s' % id)
        return False

    # Get the feature center
    extract.basemap['feature_center'] = get_feature_center(id)
    feature_center = extract.basemap['feature_center']

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
                "strokeOpacity": 0.6,
                "[INTERSECTS(geometry, "+wkt_polygon+")]": {
                    "symbolizers": [{
                        "strokeColor": "red",
                        "strokeWidth": 2,
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

    for topic in extract.topics:

        # for the federal data layers we get the restrictions calling the feature service and store the result in the DB
        if topic.topicid in extract.baseconfig['ch_topics']:
            xml_layers = []
            for xml_layer in topic.layers:
                xml_layers.append(xml_layer.layername)
            #  get_XML(feature['geom'], topic.topicid, extractcreationdate, lang, translations)

        topicdata[str(topic.topicid)] = {
            "categorie": 0,
            "docids": set([]),
            "topicname": topic.topicname,
            "bboxlegend": [],
            "layers": {},
            "legalbase": [],
            "legalprovision": [],
            "reference": [],
            "authority": {
                "authorityuuid": topic.authority.authorityid,
                "authorityname": topic.authority.authorityname,
                "authorityurl": topic.authority.authoritywww
                },
            "topicorder": topic.topicorder,
            "authorityfk": topic.authorityfk,
            "publicationdate": topic.publicationdate
            }

        # if geographic layers are defined for the topic, get the list of all layers and then
        # check for each layer the information regarding the features touching the property
        if topic.layers:
            topicdata[str(topic.topicid)]['wmslayerlist'] = []

            for layer in topic.layers:
                topicdata[str(topic.topicid)]["layers"][layer.layerid] = {
                    "layername": layer.layername,
                    "features": None
                    }
                topicdata[str(topic.topicid)]['wmslayerlist'].append(layer.layername)

                # intersects a given layer with the feature and adds the results to the topicdata- see method add_layer
                layerdata = add_layer(layer, propertynumber, featureinfo, translations, appconfig, topicdata)
                if layerdata is not None:
                    topicdata[str(topic.topicid)]['layers'][layer.layerid]['features'] = layerdata[str(layer.layerid)]['features']
                    topicdata[str(topic.topicid)]['categorie'] = 3
                    for restrictionid in layerdata[str(layer.layerid)]['ids']:
                        docfilters = [restrictionid]
                        for doctype in appconfig['doctypes'].split(','):
                            docfilters.append(doctype)
                            docidlist = get_document_ref(docfilters)
                            docs = set_documents(str(layer.topicfk), doctype, docidlist, featureinfo, False, topicdata[str(topic.topicid)]['docids'])
                            for doc in docs:
                                topicdata[str(topic.topicid)]['docids'].add(doc['documentid'])
                                del doc['documentid']
                                topicdata[str(topic.topicid)][doctype].append(doc)
                else:
                    topicdata[str(topic.topicid)]['layers'][layer.layerid] = {'layername': layer.layername, 'features': None}
                    if topicdata[str(topic.topicid)]['categorie'] != 3:
                        topicdata[str(topic.topicid)]['categorie'] = 1

                # get the legend entries in the map bbox not touching the features
                featurelegend = get_legend_classes(to_shape(featureinfo['geom']), layer.layername, translations, extract.srid)
                bboxlegend = get_legend_classes(to_shape(WKTElement(map_bbox)), layer.layername, translations, extract.srid)
                bboxitems = set()
                for legenditem in bboxlegend:
                    if legenditem not in featurelegend:
                        bboxitems.add(tuple(legenditem.items()))
                if len(bboxitems) > 0:
                    for el in bboxitems:
                        legendclass = dict((x, y) for x, y in el)
                        legendclass['codegenre'] = legenddir+legendclass['codegenre']+".png"
                        topicdata[str(topic.topicid)]["bboxlegend"].append(legendclass)
            # Get the list of documents related to a topic with layers and results
            if topicdata[str(layer.topicfk)]["categorie"] == 3:
                docfilters = [str(topic.topicid)]
                for doctype in appconfig["doctypes"].split(','):
                    docidlist = get_document_ref(docfilters)
                    docs = set_documents(str(topic.topicid), doctype, docidlist, featureinfo, True, topicdata[str(topic.topicid)]['docids'])
                    for doc in docs:
                        topicdata[str(topic.topicid)]['docids'].add(doc['documentid'])
                        del doc['documentid']
                        topicdata[str(topic.topicid)][doctype].append(doc)
        else:
            if str(topic.topicid) in appconfig['emptytopics']:
                emptytopics.append(topic.topicname)
                topicdata[str(topic.topicid)]['layers'] = None
                topicdata[str(topic.topicid)]['categorie'] = 0
            else:
                topicdata[str(topic.topicid)]['layers'] = None
                topicdata[str(topic.topicid)]['categorie'] = 1

        if topicdata[str(topic.topicid)]['categorie'] == 1:
            notconcernedtopics.append(topic.topicname)

        if topicdata[topic.topicid]["categorie"] == 3:
            appendiceslist = []

            for i, legalprovision in enumerate(topicdata[str(topic.topicid)]["legalprovision"]):
                if legalprovision["officialtitle"] != "":
                    appendiceslist.append(['A'+str(i+1), legalprovision["officialtitle"]])
            for doctype in appconfig["doctypes"].split(','):
                if topicdata[str(topic.topicid)][doctype] == []:
                    topicdata[str(topic.topicid)][doctype] = [{
                        "officialtitle": "",
                        "title": "",
                        "remoteurl": ""
                    }]

            concernedtopics.append({
                "topicname": topic.topicname,
                "documentlist": {
                    "columns": ["appendixno", "appendixtitle"],
                    "data": appendiceslist
                }
            })

            if topicdata[topic.topicid]['layers']:
                topicdata[str(topic.topicid)]["restrictions"] = []

                for layer in topicdata[topic.topicid]['layers']:
                    if topicdata[topic.topicid]['layers'][layer]['features']:
                        for feature in topicdata[topic.topicid]['layers'][layer]['features']:
                            if 'teneur' in feature.keys() and feature['teneur'] is not None and feature['statutjuridique'] is not None:
                                if feature['codegenre'] is None:
                                    feature['codegenre'] = '9999'
                                if isinstance(feature['codegenre'], int):
                                    feature['codegenre'] = str(feature['codegenre'])
                                if feature['geomType'] == 'area':
                                    topicdata[str(topic.topicid)]["restrictions"].append({
                                        "codegenre": legenddir+feature['codegenre']+".png",
                                        "teneur": feature['teneur'],
                                        "area": feature['intersectionMeasure'].replace(' : ', '').replace(' - ', '').replace('[m2]', 'm<sup>2</sup>'),
                                        "area_pct": round((float(
                                            feature['intersectionMeasure'].replace(' : ', '').replace(' - ', '').replace(' [m2]', ''))*100)/propertyarea, 1)
                                    })
                                else:
                                    topicdata[str(topic.topicid)]["restrictions"].append({
                                        "codegenre": legenddir+feature['codegenre']+".png",
                                        "teneur": feature['teneur'],
                                        "area": feature['intersectionMeasure'].replace(' - ', '').replace(' : ', '').replace('[m]', 'm'),
                                        "area_pct": -1
                                    })
                            else:
                                for property, value in feature.iteritems():
                                    if value is not None and property != 'featureClass':
                                        if isinstance(value, float) or isinstance(value, int):
                                            value = str(value)
            topiclayers = {
                "baseURL": request.registry.settings['crdppf_wms'],
                "opacity": 1,
                "type": "WMS",
                "layers": topicdata[str(topic.topicid)]['wmslayerlist'],
                "imageFormat": "image/png",
                "styles": "default",
                "customParams": {
                    "TRANSPARENT": "true"
                }
            }

            # This define the "general" map that we are going to copy x times,
            # one time as base map and x times as topic map.
            map = {
                "projection": "EPSG:"+str(extract.srid),
                "dpi": 150,
                "rotation": 0,
                "center": feature_center,
                "scale": print_box['scale']*map_buffer,
                "longitudeFirst": "true",
                "layers": [
                    {
                        "type": "geojson",
                        "geoJson": request.route_url('get_property')+'?id='+id,
                        "style": {
                            "version": "2",
                            "strokeColor": "gray",
                            "strokeLinecap": "round",
                            "strokeOpacity": 0.6,
                            "[INTERSECTS(geometry, "+wkt_polygon+")]": {
                                "symbolizers": [
                                    {
                                        "strokeColor": "red",
                                        "strokeWidth": 2,
                                        "type": "line"
                                    }
                                ]
                            }
                        }
                    },
                    topiclayers,
                    basemaplayers
                ]
            }

            if topicdata[str(topic.topicid)]["bboxlegend"] == []:
                topicdata[str(topic.topicid)]["bboxlegend"] = [{
                    "codegenre": "",
                    "teneur": ""
                    }]

            data.append({
                "topicname": topic.topicname,
                "map": map,
                "restrictions": topicdata[str(topic.topicid)]["restrictions"],
                "bboxlegend": topicdata[str(topic.topicid)]["bboxlegend"],
                "completelegend": extract.topiclegenddir+str(topic.topicid)+'_topiclegend.pdf',
                "legalbases": topicdata[str(topic.topicid)]["legalbase"],
                "legalprovisions": topicdata[str(topic.topicid)]["legalprovision"],
                "references": topicdata[str(topic.topicid)]["reference"],
                "authority": [
                    topicdata[str(topic.topicid)]["authority"]
                ]
            })

    d = {
        "attributes": {
            "reporttype": type,
            "directprint": directprint,
            "extractcreationdate": extract.creationdate,
            "filename": extract.filename,
            "extractid": extract.id,
            "map": basemap,
            "municipality": municipality,
            "cadastre": cadastre,
            "cadastrelabel": "Cadastre",
            "propertytype": propertytype,
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

    # import json
    # pretty printed json data for the extract
    # jsonfile = open('C:/Temp/'+extract.filename+'.json', 'w')
    # jsondata = json.dumps(d, indent=4)
    # jsonfile.write(jsondata)
    # jsonfile.close()

    return d
