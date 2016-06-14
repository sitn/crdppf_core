# -*- coding: UTF-8 -*-

from copy import deepcopy
import ast
from datetime import datetime

from crdppf.lib.wmts_parsing import wmts_layer
from crdppf.lib.geometry_functions import get_feature_bbox, get_print_format, get_feature_center

from crdppf.views.get_features import get_features_function
from crdppf.util.documents import get_document_ref, get_documents
from crdppf.util.pdf_functions import get_feature_info, get_translations, get_XML

from crdppf.models import DBSession,Topics,AppConfig

import logging

log = logging.getLogger(__name__)

def set_documents(request, topicid, doctype, docids, featureInfo, geofilter):
    """ Function to fetch the documents related to the restriction:
    legal provisions, temporary provisions, references 
    """

    docs = {}
    documents = []
    
    if geofilter is True:
        filters = {
            'docids': docids,
            'topicid': topicid,
            'cadastrenb': featureInfo['numcom'],
            'chmunicipalitynb': featureInfo['nufeco']
        }
    else:
        filters = {'docids':docids}

    if len(docids) > 0:
        docs = get_documents(filters)
    else:
        docs['docs'] = []

    references = []
    # store the documents in a list
    if len(docs['docs']) > 0:
        for doc in docs['docs']:
            if doc['doctype'] == doctype and doc['documentid'] in docids:
                references.append(doc)
                if doc['doctype'] != u'legalbase' and doc['documentid'] not in self.doclist:
                    self.add_appendix(topicid, 'A'+str(len(self.appendix_entries)+1), unicode(doc['officialtitle']).encode('iso-8859-1'), unicode(doc['remoteurl']).encode('iso-8859-1'), doc['localurl'])
                if doc['documentid'] not in self.doclist:
                    self.doclist.append(doc)
            if doc['doctype'] == doctype and geofilter is True and doc['documentid'] not in docids:
                references.append(doc)
                if doc['doctype'] != u'legalbase' and doc['documentid'] not in self.doclist:
                    self.add_appendix(topicid, 'A'+str(len(self.appendix_entries)+1), unicode(doc['officialtitle']).encode('iso-8859-1'), unicode(doc['remoteurl']).encode('iso-8859-1'), doc['localurl'])
                if doc['documentid'] not in self.doclist:
                    self.doclist.append(doc)
                    
    return references
        
def add_toc_entry(topicid, num, label, categorie, appendices):
    tocentries = {}
    tocentries[str(topicid)]={'no_page':num, 'title':label, 'categorie':int(categorie), 'appendices':set()}
    
    return tocentries

def add_layer(request, layer, featureid, featureInfo, translations, appconfig, topiclist):

    layerlist = {}
    
    results = get_features_function(featureInfo['geom'],{'layerList':layer.layername,'id':featureid,'translations':translations})

    if results :
        layerlist[str(layer.layerid)]={'layername':layer.layername,'features':[]}
        for result in results:
            # for each restriction object we check for related documents
            docfilters = [str(result['id'])]
            for doctype in appconfig['doctypes']:
                docidlist = get_document_ref(docfilters)
                result['properties'][doctype] = set_documents(request, str(layer.topicfk), doctype, docidlist, featureInfo, False)
            layerlist[str(layer.layerid)]['features'].append(result['properties'])

        # we also check for documents on the layer level - if there are any results - else we don't need to bother
        docfilters = [layer.layername]
        for doctype in appconfig['doctypes']:
            docidlist = get_document_ref(docfilters)
            topiclist[str(layer.topicfk)]['layers'][layer.layerid][doctype] = set_documents(request, str(layer.topicfk), doctype, docidlist, featureInfo, True)

        topiclist[str(layer.topicfk)]['categorie']=3
        topiclist[str(layer.topicfk)]['no_page']='tocpg_'+str(layer.topicfk)
        topiclist[str(layer.topicfk)]['layers'][layer.layerid]['features'] = layerlist[str(layer.layerid)]['features']
    else:
        layerlist[str(layer.layerid)]={'layername':layer.layername,'features':None}
        if topiclist[str(layer.topicfk)]['categorie'] != 3:
            topiclist[str(layer.topicfk)]['categorie']=1
    
    return topiclist
    
def get_content(idemai, request):
    """ TODO....
        Explain how the whole thing works...
    """
    # Start a session
    session = request.session
    configs = DBSession.query(AppConfig).all()
    
    appconfig = {}
    for config in configs:
        if not config.parameter in [u'crdppflogopath', u'cantonlogopath']:
            appconfig[config.parameter] = config.paramvalue
    extract = {}
    extractcreationdate = datetime.now().strftime("%Y%m%d%H%M%S")
    extract['pdfid'] = extractcreationdate

    # Define language to get multilingual labels for the selected language
    # defaults to 'fr': french - this may be changed in the appconfig
    if 'lang' not in session:
        lang = request.registry.settings['default_language'].lower()
    else : 
        lang = session['lang'].lower()
    translations = get_translations(lang)
    appconfig['translations'] = translations

    
    # 1) If the ID of the parcel is set get the basic attributs of the property
    # else get the ID (idemai) of the selected parcel first using X/Y coordinates of the center 
    #----------------------------------------------------------------------------------------------------
    featureInfo = get_feature_info(idemai,translations) # '1_14127' # test parcel or '1_11340'
    extract['featureInfo'] = featureInfo
    
    # 3) Get the list of all the restrictions by topicorder set in a column
    #-------------------------------------------
    topics = DBSession.query(Topics).order_by(Topics.topicorder).all()
    
    # Configure the WMTS background layer
    url = request.registry.settings['wmts_getcapabilities_url']
    defaultTiles =  ast.literal_eval("{"+request.registry.settings['defaultTiles']+"}")
    layer = defaultTiles['wmtsname']
    wmts_layer_ = wmts_layer(url, layer)

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

    basemap = {
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
        
    data = []
    topiclist = {}

    for topic in topics:
        layers = []

        # for the federal data layers we get the restrictions calling the feature service and store the result in the DB
        #~ if topic.topicid in appconfig['ch_topics']:
            #~ xml_layers = []
            #~ for xml_layer in topic.layers:
                #~ xml_layers.append(xml_layer.layername)
            #~ get_XML(featureInfo['geom'], topic.topicid, extractcreationdate, lang, translations)

        topiclist[str(topic.topicid)]={
            'categorie':0,
            'topicname':topic.topicname,
            'layers':{},
            'authority':topic.authority, 
            'topicorder':topic.topicorder,
            'authorityfk':topic.authorityfk,
            'publicationdate':topic.publicationdate
            }

        toc_entries = {}
        # if geographic layers are defined for the topic, get the list of all layers and then
        # check for each layer the information regarding the features touching the property
        if topic.layers:
            add_toc_entry(topic.topicid, '', str(topic.topicname.encode('iso-8859-1')), 1, '')
            for layer in topic.layers:
                topiclist[str(topic.topicid)]['layers'][layer.layerid]={
                    'layername':layer.layername,
                    'features':None
                    }
                # intersects a given layer with the feature and adds the results to the topiclist- see method add_layer
                toto = add_layer(request, layer, propertynumber, featureInfo, translations, appconfig, topiclist)
                topiclist.update(add_layer(request, layer, propertynumber, featureInfo, translations, appconfig, topiclist))
            #~ get_topic_map(topic.layers, topic.topicid)
            # Get the list of documents related to a topic with layers and results
            if topiclist[str(layer.topicfk)]['categorie'] == 3:
                docfilters = [str(topic.topicid)]
                for doctype in appconfig['doctypes']:
                    docidlist = get_document_ref(docfilters)
                    #~ topiclist[str(topic.topicid)][doctype] = set_documents(request, str(topic.topicid), doctype, docidlist, featureInfo, True)      

        else:
            if str(topic.topicid) in appconfig['emptytopics']:
                topiclist[str(topic.topicid)]['layers'] = None
                topiclist[str(topic.topicid)]['categorie'] = 1
            else:
                topiclist[str(topic.topicid)]['layers'] = None
                topiclist[str(topic.topicid)]['categorie'] = 0

        data.append({
            'topic_title': topic.topicname,
            'table' : {
                'columns': ["id", "name", "icon"],
                'data': [
                    [1, "blah", "icon_pan"],
                    [2, "blip", "icon_zoomin"]
                    ]
                }
            #~ topic.topicorder,
            #~ layers
            #'topiclist': topiclist,
            })
            
    #~ data.append(
        #~ {
        #~ 'topic_title': 'titre1',
        #~ 'topic_text': 'topicorder',
        #~ 'topic_layers': 'layer',
        #~ 'topiclist': topiclist,
        #~ 'map': map
        #~ })

    d = {
    #    "datasource": [],
        "map": map
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
