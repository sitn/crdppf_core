# -*- coding: UTF-8 -*-

import json
from copy import deepcopy
import ast
from datetime import datetime

from crdppf import db_config
from crdppf.extract import Extract
from crdppf.lib.wmts_parsing import wmts_layer
from crdppf.lib.geometry_functions import get_feature_bbox, get_print_format, get_feature_center

from crdppf.views.get_features import get_features_function
from crdppf.util.documents import get_document_ref, get_documents
from crdppf.util.pdf_functions import get_feature_info, get_translations
from crdppf.util.pdf_functions import geom_from_coordinates, get_XML

from crdppf.models import DBSession,Topics,AppConfig

from geoalchemy2 import functions, WKTElement
from geoalchemy2.shape import to_shape
import logging

log = logging.getLogger(__name__)
    
def set_documents(request, topicid, doctype, docids, featureinfo, geofilter, topicdata):
    """ Function to fetch the documents related to the restriction:
    legal provisions, temporary provisions, references 
    """

    docs = []
    documents = []
    doclist = topicdata["doclist"]
    
    if geofilter is True:
        filters = {
            "docids": docids,
            "topicid": topicid,
            "cadastrenb": featureinfo["numcom"],
            "chmunicipalitynb": featureinfo["nufeco"]
        }
    else:
        filters = {"docids":docids}

    if len(docids) > 0:
        docs = get_documents(filters)
    else:
        docs = []

    appendices = []

    # store the documents in a list
    if len(docs) > 0:
        doc = ""
        for doc in docs:
            if doc['doctype'] == doctype and doc['documentid'] in docids:
                documents.append({"officialtitle": doc['officialtitle'], "remoteurl": doc['remoteurl']})
                if doc['doctype'] != u'legalbase' and doc['documentid'] not in doclist:
                    appendices.append(add_appendix(topicid, 'A'+str(len(appendices)+1), unicode(doc['officialtitle']).encode('iso-8859-1'), unicode(doc['remoteurl']).encode('iso-8859-1'), doc['localurl'], topicdata))
                if doc['documentid'] not in doclist:
                    doclist.append(doc)
            if doc['doctype'] == doctype and geofilter is True and doc['documentid'] not in docids:
                documents.append({"officialtitle": doc['officialtitle'], "remoteurl": doc['remoteurl']})
                if doc['doctype'] != u'legalbase' and doc['documentid'] not in doclist:
                    appendices.append(add_appendix(topicid, 'A'+str(len(appendices)+1), unicode(doc['officialtitle']).encode('iso-8859-1'), unicode(doc['remoteurl']).encode('iso-8859-1'), doc['localurl'], topicdata))
                if doc['documentid'] not in doclist:
                    doclist.append(doc)
    if documents == []:
        documents = [{"officialtitle": "", "remoteurl": ""}]

    return documents

def add_toc_entry(topicid, num, label, categorie, appendices):
    tocentries = {}
    tocentries[str(topicid)]={'no_page':num, 'title':label, 'categorie':int(categorie), 'appendices':set()}

    return tocentries

def add_appendix(topicid, num, label, url, filepath, topicdata):
    toc_entries = topicdata['toc_entries']
    appendix_entries = []
    appendix_entries.append({'topicid':topicid, 'no_page':num, 'title':label, 'url':url, 'path':filepath})

    if topicid in toc_entries[topicid] :
        toc_entries[topicid]['appendices'].add(num)
    else:
        pass

    return appendix_entries

def get_legend_classes(bbox, layername, translations):
    """ Collects all the features in the map perimeter into a list to create a dynamic legend
    """
    # transform coordinates from wkt to SpatialElement for intersection
    polygon = WKTElement(bbox.wkt, 2056)
    mapfeatures = get_features_function(polygon, {'layerList':layername, 'translations': translations})
    if mapfeatures is not None:
        classes = []
        for mapfeature in mapfeatures:
            if mapfeature['properties'] is None:
                mapfeature['properties'] = '9999'
            if isinstance(mapfeature['properties'],int):
                mapfeature['properties'] = str(feature['codegenre'])
            classes.append({"codegenre": str(mapfeature['properties']['codegenre']), "teneur": mapfeature['properties']['teneur']})

    return classes

def add_layer(request, layer, featureid, featureinfo, translations, appconfig, topicdata):

    layerlist = {}
    results = get_features_function(featureinfo['geom'],{'layerList':layer.layername,'id':featureid, 'translations':appconfig['translations']})

    if results :
        layerlist[str(layer.layerid)]={'layername':layer.layername,'features':[]}
        for result in results:
            # for each restriction object we check for related documents
            docfilters = [str(result['id'])]
            for doctype in appconfig['doctypes'].split(','):
                docfilters.append(doctype)
                docidlist = get_document_ref(docfilters)
                result['properties'][doctype] = set_documents(request, str(layer.topicfk), doctype, docidlist, featureinfo, False, topicdata)
            layerlist[str(layer.layerid)]['features'].append(result['properties'])

        # we also check for documents on the layer level - if there are any results - else we don't need to bother
        docfilters = [layer.layername]
        for doctype in appconfig['doctypes'].split(','):
            docfilters.append(doctype)
            docidlist = get_document_ref(docfilters)
            topicdata[str(layer.topicfk)]['layers'][layer.layerid][doctype] = set_documents(request, str(layer.topicfk), doctype, docidlist, featureinfo, True,  topicdata)

        topicdata[str(layer.topicfk)]['categorie']=3
        topicdata[str(layer.topicfk)]['no_page']='tocpg_'+str(layer.topicfk)
        topicdata[str(layer.topicfk)]['layers'][layer.layerid]['features'] = layerlist[str(layer.layerid)]['features']
    else:
        layerlist[str(layer.layerid)]={'layername': layer.layername,'features': None}
        if topicdata[str(layer.topicfk)]['categorie'] != 3:
            topicdata[str(layer.topicfk)]['categorie']=1

    return topicdata

def get_content(id, request):
    """ TODO....
        Explain how the whole thing works...
    """
    # Start a session
    session = request.session
    configs = DBSession.query(AppConfig).all()

    # initalize extract object
    extract = Extract(request)

    for config in configs:
        if not config.parameter in ['crdppflogopath', 'cantonlogopath']:
            extract.baseconfig[config.parameter] = config.paramvalue
    extract.srid = db_config['srid']

    extract.topiclegenddir = request.static_url('crdppf:static/public/legend/')

    # Define language to get multilingual labels for the selected language
    # defaults to 'fr': french - this may be changed in the appconfig
    if 'lang' not in session:
        extract.baseconfig['lang'] = request.registry.settings['default_language'].lower()
    else : 
        extract.baseconfig['lang']  = session['lang'].lower()
    extract.baseconfig['translations'] = get_translations(extract.baseconfig['lang'])
    # for simplification
    translations = extract.baseconfig['translations'] 

    # 1) If the ID of the parcel is set get the basic attributs of the property
    # else get the ID (id) of the selected parcel first using X/Y coordinates of the center 
    #----------------------------------------------------------------------------------------------------
    featureinfo = get_feature_info(id, extract.srid, translations) # '1_14127' # test parcel or '1_11340'
    featureinfo = featureinfo
    extract.filename = extract.id + featureinfo['featureid']

    # 3) Get the list of all the restrictions by topicorder set in a column
    #-------------------------------------------
    extract.topics = DBSession.query(Topics).order_by(Topics.topicorder).all()

    # Configure the WMTS background layer
    defaultTiles = ast.literal_eval("{"+request.registry.settings['defaultTiles']+"}")
    wmts = {
        'url': request.registry.settings['wmts_getcapabilities_url'],
        'defaultTiles': defaultTiles,
        'layer': defaultTiles['wmtsname']
    }

    wmts_layer_= wmts_layer(wmts['url'], wmts['layer'])
    extract.baseconfig['wmts'] = wmts

    municipality = featureinfo['nomcom'].strip()
    cadastre = featureinfo['nomcad'].strip()
    propertynumber = featureinfo['nummai'].strip()
    propertytype = featureinfo['type'].strip()
    propertyarea = featureinfo['area']
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
        "projection": "EPSG:2056",
        "dpi": 150,
        "rotation": 0,
        "center": feature_center,
        "scale": print_box['scale']*1.5,
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
    topicdata["toc_entries"] = {}
    topicdata["doclist"] = []
    topicdata["appendix_entries"] = []
    appconfig = extract.baseconfig
    concernedtopics = []
    notconcernedtopics = []
    emptytopics = []

    for topic in extract.topics:
        layers = []

        # for the federal data layers we get the restrictions calling the feature service and store the result in the DB
        if topic.topicid in extract.baseconfig['ch_topics']:
            xml_layers = []
            for xml_layer in topic.layers:
                xml_layers.append(xml_layer.layername)
            #~ get_XML(feature['geom'], topic.topicid, extractcreationdate, lang, translations)

        topicdata[str(topic.topicid)]={
            "categorie": 0,
            "topicname": topic.topicname,
            "bboxlegend": [{"codegenre": "", "teneur": ""}],
            "layers": {},
            "legalbase": {},
            "legalprovision": [{
                    "officialtitle": "",
                    "remoteurl": ""
                }],
            "reference": [{
                    "officialtitle": "",
                    "remoteurl": ""
                }],
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
            topicdata["toc_entries"].update(add_toc_entry(topic.topicid, '', str(topic.topicname.encode('iso-8859-1')), 1, ''))

            for layer in topic.layers:
                topicdata[str(topic.topicid)]["layers"][layer.layerid]={
                    "layername": layer.layername,
                    "features": None
                    }
                topicdata[str(topic.topicid)]['wmslayerlist'].append(layer.layername)
                # intersects a given layer with the feature and adds the results to the topicdata- see method add_layer
                topicdata[str(topic.topicid)].update(add_layer(request, layer, propertynumber, featureinfo, translations, appconfig, topicdata))

                # get the legend entries in the map bbox not touching the features
                featurelegend = get_legend_classes(to_shape(featureinfo['geom']),layer.layername,translations)
                bboxlegend = get_legend_classes(to_shape(WKTElement(wkt_polygon)),layer.layername,translations)
                bboxitems = set()
                for legenditem in bboxlegend:
                    if not legenditem in featurelegend:
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
                    topicdata[str(topic.topicid)][doctype] = set_documents(request, str(topic.topicid), doctype, docidlist, featureinfo, True, topicdata)

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
            
        if topicdata[str(topic.topicid)]['categorie']  == 0:
            emptytopics.append(topic.topicname)

        if topicdata[topic.topicid]["categorie"] == 3:
            appendiceslist = []
            i=0
            for legalprovision in topicdata[str(topic.topicid)]["legalprovision"]:
                if not legalprovision["officialtitle"] == "":
                    i += 1
                    appendiceslist.append('A'+str(i)+' '+legalprovision["officialtitle"])
            concernedtopics.append({
                    "topicname": topic.topicname,
                    "documentlist" : ";".join(appendiceslist)
                })

            if topicdata[topic.topicid]['layers']:
                topicdata[str(topic.topicid)]["restrictions"] = []
                
                for layer in topicdata[topic.topicid]['layers']:
                    if topicdata[topic.topicid]['layers'][layer]['features']:
                        for feature in topicdata[topic.topicid]['layers'][layer]['features']:
                            if 'teneur' in feature.keys() and feature['teneur'] is not None and feature['statutjuridique'] is not None:
                                if feature['codegenre'] is None:
                                    feature['codegenre'] = '9999'
                                if isinstance(feature['codegenre'],int):
                                    feature['codegenre'] = str(feature['codegenre'])
                                if feature['geomType'] == 'area' :
                                    topicdata[str(topic.topicid)]["restrictions"].append({
                                        "codegenre": legenddir+feature['codegenre']+".png",
                                        "teneur": feature['teneur'],
                                        "area": feature['intersectionMeasure'].replace(' : ','').replace(' - ',''),
                                        "area_pct": round((float(feature['intersectionMeasure'].replace(' : ','').replace(' - ','').replace(' [m2]',''))*100)/propertyarea,1)
                                    })
                                else: 
                                    topicdata[str(topic.topicid)]["restrictions"].append({
                                        "codegenre": legenddir+feature['codegenre']+".png",
                                        "teneur": feature['teneur'],
                                        "area": feature['intersectionMeasure'].replace(' - ','').replace(' : ',''),
                                        "area_pct": 0
                                    })
                            else:
                                for property,value in feature.iteritems():
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
                "projection": "EPSG:2056",
                "dpi": 150,
                "rotation": 0,
                "center": feature_center,
                "scale": print_box['scale']*1.1,
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
                                "strokeColor": "green",
                                "strokeWidth": 2,
                                "type": "line"
                            }]
                        }
                    }
                }, 
                topiclayers, 
                wmts_layer_
                ]
            }

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

            appendices = {
                "topicid": str(topic.topicid),
                "documentlist" : topicdata[str(topic.topicid)]["legalprovision"]
                }

    d= {
        "attributes": {
            "extractcreationdate": extract.creationdate,
            "filename": extract.filename,
            "extractid": extract.id,
            "map": basemap,
            "municipality": municipality,
            "cadastre": cadastre,
            "cadastrelabel": "Cadastre",
            "propertytype": propertytype,
            "propertynumber": propertynumber,
            "EGRIDnumber": featureinfo['no_egrid'],
            "municipalitylogopath": municipalitylogopath,
            "federalmunicipalitynumber": featureinfo['nufeco'],
            "competentauthority": extract.baseconfig['competentauthority'] ,
            "title": report_title,
            "toc": [{
                "concernedtopics":  concernedtopics,
                "notconcernedtopics": ";".join(notconcernedtopics),
                "emptytopics": ";".join(emptytopics)
            }],
            "propertyarea": propertyarea,
            "datasource": data
        },
        "layout": "report",
        "outputFormat": "pdf"
    }
    #~ sdf

    # pretty printed json data for the extract
    #~ jsonfile = open('C:/Temp/extractdata.json', 'w')
    #~ jsondata = json.dumps(d['attributes'], indent=4)
    #~ jsonfile.write(jsondata)
    #~ jsonfile.close()

    return d
