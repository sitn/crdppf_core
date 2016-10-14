# -*- coding: UTF-8 -*-

from copy import deepcopy
import ast
from datetime import datetime

from crdppf.extract import Extract
from crdppf.lib.wmts_parsing import wmts_layer
from crdppf.lib.geometry_functions import get_feature_bbox, get_print_format, get_feature_center

from crdppf.views.get_features import get_features_function
from crdppf.util.documents import get_document_ref, get_documents
from crdppf.util.pdf_functions import get_feature_info, get_translations, get_XML

from crdppf.models import DBSession,Topics,AppConfig

import logging

log = logging.getLogger(__name__)

#~ def get_topiclist():
    #~ topics = DBSession.query(Topics).order_by(Topics.topicorder).all()
    
    #~ topiclist = {}
    #~ for topic in topics:
        #~ topiclist[topic.topicorder] = {
            #~ 'topicid': topic.topicid,
            #~ 'topicname': topic.topicname,
            #~ 'layers': topic.layers,
            #~ 'publicationdate': topic.publicationdate.isoformat() if topic.publicationdate else None,
            #~ 'authorityfk': topic.authorityfk,
            #~ 'authority': topic.authority,
            #~ 'metadata': topic.metadata
            #~ }

    #~ return topiclist
    
def set_documents(request, topicid, doctype, docids, featureinfo, geofilter, topicdata):
    """ Function to fetch the documents related to the restriction:
    legal provisions, temporary provisions, references 
    """

    docs = []
    documents = []
    doclist = topicdata['doclist']
    
    if geofilter is True:
        filters = {
            'docids': docids,
            'topicid': topicid,
            'cadastrenb': featureinfo['numcom'],
            'chmunicipalitynb': featureinfo['nufeco']
        }
    else:
        filters = {'docids':docids}

    if len(docids) > 0:
        docs = get_documents(filters)
    #~ else:
        #~ docs = []
    data = []
    columns = []
    references = []
    appendices = []
    # store the documents in a list
    if len(docs) > 0:
        for doc in docs:
            if doc['doctype'] == doctype and doc['documentid'] in docids:
                references.append(doc)
                if doc['doctype'] != u'legalbase' and doc['documentid'] not in doclist:
                    appendices.append(add_appendix(topicid, 'A'+str(len(appendices)+1), unicode(doc['officialtitle']).encode('iso-8859-1'), unicode(doc['remoteurl']).encode('iso-8859-1'), doc['localurl'], topicdata))
                if doc['documentid'] not in doclist:
                    doclist.append(doc)
            if doc['doctype'] == doctype and geofilter is True and doc['documentid'] not in docids:
                references.append(doc)
                if doc['doctype'] != u'legalbase' and doc['documentid'] not in doclist:
                    appendices.append(add_appendix(topicid, 'A'+str(len(appendices)+1), unicode(doc['officialtitle']).encode('iso-8859-1'), unicode(doc['remoteurl']).encode('iso-8859-1'), doc['localurl'], topicdata))
                if doc['documentid'] not in doclist:
                    doclist.append(doc)

        columns = doclist[0].keys()
        for document in doclist:
            data.append([document['officialtitle'], document['remoteurl']])
        references = {"columns": ["officialtitle","remoteurl"], "data": data}

    return references
        
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

def add_layer(request, layer, featureid, featureinfo, translations, appconfig, topicdata):

    layerlist = {}
    
    results = get_features_function(featureinfo['geom'],{'layerList':layer.layername,'id':featureid, 'translations':appconfig['translations']})
    if results :
        layerlist[str(layer.layerid)]={'layername':layer.layername,'features':[]}
        for result in results:
            # for each restriction object we check for related documents
            docfilters = [str(result['id'])]
            for doctype in appconfig['doctypes'].split(','):
                docidlist = get_document_ref(docfilters)
                result['properties'][doctype] = set_documents(request, str(layer.topicfk), doctype, docidlist, featureinfo, False, topicdata)
            layerlist[str(layer.layerid)]['features'].append(result['properties'])

        # we also check for documents on the layer level - if there are any results - else we don't need to bother
        docfilters = [layer.layername]
        for doctype in appconfig['doctypes'].split(','):
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
    
def get_content(idemai, request):
    """ TODO....
        Explain how the whole thing works...
    """
    # Start a session
    session = request.session
    configs = DBSession.query(AppConfig).all()
    
    # initalize extract object
    extract = Extract(request)
    
    for config in configs:
        if not config.parameter in [u'crdppflogopath', u'cantonlogopath']:
            extract.baseconfig[config.parameter] = config.paramvalue
    extract.id = extract.timestamp

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
    # else get the ID (idemai) of the selected parcel first using X/Y coordinates of the center 
    #----------------------------------------------------------------------------------------------------
    featureinfo = get_feature_info(idemai,translations) # '1_14127' # test parcel or '1_11340'
    featureinfo = featureinfo
    extract.filename = extract.id + u'_' + featureinfo['featureid']
    
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

    # Get the raw feature BBOX
    extract.basemap['bbox'] = get_feature_bbox(idemai)
    bbox = extract.basemap['bbox'] 
    
    if bbox is False:
        log.warning('Found more then one bbox for idemai: %s' % idemai)
        return False

    # Get the feature center
    extract.basemap['feature_center'] = get_feature_center(idemai)
    feature_center = extract.basemap['feature_center']

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
        "scale": print_box['scale']*2,
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
                        "strokeColor": "red",
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
    topicdata = {}
    topicdata['toc_entries'] = {}
    topicdata['doclist'] = []
    topicdata['appendix_entries'] = []
    appconfig = extract.baseconfig

    for topic in extract.topics:
        layers = []

        # for the federal data layers we get the restrictions calling the feature service and store the result in the DB
        if topic.topicid in extract.baseconfig['ch_topics']:
            xml_layers = []
            for xml_layer in topic.layers:
                xml_layers.append(xml_layer.layername)
            #~ get_XML(feature['geom'], topic.topicid, extractcreationdate, lang, translations)

        topicdata[str(topic.topicid)]={
            'categorie':0,
            'topicname':topic.topicname,
            'layers':{},
            'authority': {
                'authorityuuid': topic.authority.authorityid,
                'authorityname': topic.authority.authorityname,
                'authorityurl': topic.authority.authoritywww
                }, 
            'topicorder':topic.topicorder,
            'authorityfk':topic.authorityfk,
            'publicationdate':topic.publicationdate
            }

        # if geographic layers are defined for the topic, get the list of all layers and then
        # check for each layer the information regarding the features touching the property
        if topic.layers:
            topicdata['toc_entries'].update(add_toc_entry(topic.topicid, '', str(topic.topicname.encode('iso-8859-1')), 1, ''))
            for layer in topic.layers:
                topicdata[str(topic.topicid)]['layers'][layer.layerid]={
                    'layername': layer.layername,
                    'features': None
                    }
                # intersects a given layer with the feature and adds the results to the topicdata- see method add_layer
                topicdata[str(topic.topicid)].update(add_layer(request, layer, propertynumber, featureinfo, translations, appconfig, topicdata))
            #~ get_topic_map(topic.layers, topic.topicid)
            # Get the list of documents related to a topic with layers and results
            if topicdata[str(layer.topicfk)]['categorie'] == 3:
                docfilters = [str(topic.topicid)]
                for doctype in appconfig['doctypes'].split(','):
                    docidlist = get_document_ref(docfilters)
                    topicdata[str(topic.topicid)][doctype] = set_documents(request, str(topic.topicid), doctype, docidlist, featureinfo, True, topicdata)
            #~ sddf

        else:
            if str(topic.topicid) in appconfig['emptytopics']:
                topicdata[str(topic.topicid)]['layers'] = None
                topicdata[str(topic.topicid)]['categorie'] = 1
            else:
                topicdata[str(topic.topicid)]['layers'] = None
                topicdata[str(topic.topicid)]['categorie'] = 0

	#~ table = topicdata[topic.topicid]['legalbase']

	if topicdata[topic.topicid]['categorie'] == 3:
		#~ table = topicdata[topic.topicid]['legalbase']
		#~ if len(table) < 1:
		table = {
				"columns": ["officialtitle","remoteurl"],
				"data": [
					[topic.topicname, "url1"],
					["Document 2", "url2"],
				]
			}
		data.append({
			"topicname": topic.topicname,
			"map": map,
			"topicdata" : [{
				"item": topic.topicname,
				"table": table
				}]
		})
			#~ "topicdata": {"item": "values"}
				#~ {
						#~ "columns": ["officialtitle","remoteurl"],
						#~ "data": [
							#~ ["Document 1", "url1"],
							#~ ["Document 2", "url2"],
						#~ ]
					#~ }
			#~ "topicname": topic.topicname,
			#~ "authority": topic.authority.authorityname,
			#~ "table" : [{
				#~ "legalbases": topicdata[topic.topicid]['legalbase'],
				#~ "legalprovisions": topicdata[topic.topicid]['legalprovision'],
				#~ "references": topicdata[topic.topicid]['reference']
				#~ }]
			#~ })
			#~ {"columns": [
				#~ "topic_title",
				#~ "restrictions",
				#~ "objectlegend",
				#~ "maplegend",
				#~ "legalprovisions",
				#~ "legalbases",
				#~ "references",
				#~ "authority"
				#~ ],

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
			"extractcreationdate": extract.creationdate,
			"filename": extract.filename,
			"basemap": basemap,
			"municipality": municipality,
			"cadastre": cadastre,
			"propertytype": propertytype,
			"propertynumber": propertynumber,
			"EGRIDnumber": featureinfo['no_egrid'],
			"municipalitylogopath": municipalitylogopath,
			"federalmunicipalitynumber": featureinfo['nufeco'],
			"competentauthority": "Placeholder",
			"title": report_title,
			"comments": "comment",
			"propertyarea": propertyarea,
			"maplegendlabel": "Autre légende (visible dans le cadre)",
			"certificationtext": "Certification selon xyz",
			"toctitle": "Sommaire des thèmes RDPPF",
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
        "layout": "report",
		"outputFormat": "pdf"
    }
    #~ sdf
    return d
