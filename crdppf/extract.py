# -*- coding: UTF-8 -*-
from sqlalchemy import or_

from geoalchemy2.shape import to_shape, WKTElement

from crdppf import db_config

from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from datetime import datetime

from crdppfportal.table2model_match import table2model_match

from crdppf.util.pdf_functions import get_translations, get_feature_info
from crdppf.util.get_feature_functions import get_features_function

from crdppf.lib.geometry_functions import get_feature_center, get_print_format

from crdppf.models import DBSession
from crdppf.models.models import Topics, Layers, OriginReference, LegalDocuments

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

# MAIN DOCUMENT
class Extract(object):
    """The main class for the extract object which collects all the data to write the report."""

    def __init__(self, request):
        # document id
        self.id = datetime.now().strftime("%Y%m%d%H%M%S")
        # sets the creation date of the PDF instance
        self.creationdate = datetime.now().strftime("%d.%m.%Y   %H:%M:%S")
        # same same but different use
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # output format of the report
        self.format = ''
        # basic configuration of the extract, like the language, translations and so on
        self.baseconfig = {}
        # empty dict for a list of  the topics and it's depending values
        self.topiclist = {}
        # dict holding the feature information
        self.feature = {}

        # initalize configuration regarding the database
        self.db_config = db_config

        # fetch the app config parameters
        self.appconfig = request.registry.settings['app_config']

        # fetch the PDF layout and configuration parameters
        self.pdfconfig = request.registry.settings['pdf_config']

        # define the folder where the legendicons are stored
        self.legenddir = '/'.join([
            request.registry.settings['localhost_url'],
            'proj/images/icons/'])

        # fetch the pyramid_oereb app settings
        self.pyramid_oereb = request.registry.settings['pyramid_oereb']

        # set the default coordinates reference system to CH1903+/LV95 - EPSG:2056
        self.srid = db_config['srid']
        self.basemap = {}

        self.wms_params = {}
        # setting the GetLegendGraphic option for a dynamic composition of the WMS URL
        self.wms_get_legend = {
            'REQUEST': 'GetLegendGraphic'
        }
        # setting the GetStyles option
        self.wms_get_styles = {
            'REQUEST': 'GetStyles'
        }
        # setting the GetMap option for the WMS
        self.wms_get_map = {
            'REQUEST': 'GetMap'
        }
        # Get language to fetch multilingual labels for the selected language
        # defaults to 'fr': french - this may be changed in the appconfig
        if 'lang' not in request.session:
            self.lang = request.registry.settings['default_language'].lower()
        else:
            self.lang = request.session['lang'].lower()
        # Get all translation strings
        self.translations = get_translations(self.lang)
        # Set extract report type: [reduced, reduced certified, complete, complete certified]
        try:
            self.reporttype = request.matchdict.get("type_")
        except:
            raise HTTPBadRequest('No valid extract type was found.')
        # Sets the real estate id if it exists. Else returns an error message.
        try:
            self.propertyid = request.matchdict.get("id")
        except:
            raise HTTPBadRequest('The real estate id could not be found.')
        # setting the default  root filename of the PDF and temporary files
        self.filename = self.id + self.propertyid

        # Gets the basic attributs of the real estate if it exists
        try:
            self.real_estate = get_feature_info(self.propertyid, self.srid, self.translations)
        except:
            raise HTTPNotFound('No real estate with the given id could be found.')

        self.print_box = self.set_print_format(request)

        # dict to recieve unique docids per topic to avoid duplicata
        self.docids = {}

        # initalisation of an list of empty topics by definition
        self.emptytopics = []

        # initalisation of an list of not concerned topics
        self.notconcernedtopics = []

        # initalisation of an list of not concerned topics
        self.concernedtopics = []

        #try:
        self.topics = self.get_topics()
        #except:
        #    raise HTTPNotFound('There is an error regarding the topics for this municipality.')

        try:
            self.layers = self.get_layers()
        except:
            raise HTTPNotFound('An error occured fetching the PLR relevant layers.')

        self.restrictions = self.get_restrictions()

        self.references = self.get_references()

        self.set_wms_params(request)
        self.set_mapbox()
        self.fetch_bbox_legend(request)
        self.set_topic_categorie()
        self.set_topic_map(request)


    def set_wms_params(self, request):
        """ Sets all the WMS base parameters from the configuration
        """

        self.wms_params['baseurl'] = request.registry.settings['crdppf_wms']


    def get_topics(self):
        """ Get the list of PLR topics
        """

        topics = DBSession.query(Topics).order_by(Topics.topicorder).all()

        if len(topics) > 0:
            topiclist = {}
            for topic in topics:

                if len(topic.layers) > 0:
                    wmslayerlist = []
                    for layer in topic.layers:
                        wmslayerlist.append(layer.layername)
                else:
                    wmslayerlist = None

                references = DBSession.query(OriginReference).filter(
                    OriginReference.fkobj==topic.topicid
                    ).order_by(OriginReference.docid).all()

                legalbases = []
                legalprovisions = []
                hints = []
                docidlist = set()

                if len(references) > 0:
                    for reference in references:
                        if reference.documents is not None:
                            docidlist.add(reference.docid)
                            if topic.topicid in self.docids.keys():
                                self.docids[topic.topicid].update(docidlist)
                            else:
                                self.docids.update({topic.topicid: docidlist})

                if topic.topicid == 'R073':
                    legendlayers = 'r73_amenagement'
                else:
                    legendlayers = ','.join(wmslayerlist)

                # TO BE DONE : put real layer list by topic
                completelegend = ''.join([
                    'https://sitn.ne.ch/ogc-pyramid-oereb-dev/wms?',
                    'SINGLETILE=true&',
                    'TRANSPARENT=true&',
                    'SERVICE=WMS&VERSION=1.1.1&',
                    'REQUEST=GetLegendGraphic&',
                    'EXCEPTIONS=application%2Fvnd.ogc.se_xml&',
                    'LAYER=',
                    legendlayers,
                    '&',
                    'FORMAT=image%2Fpng&',
                    'LEGEND_OPTIONS=forceLabels%3Aon&',
                    'WIDTH=200&HEIGHT=100'])

                self.topiclist[topic.topicorder] = {
                    'categorie': 0,
                    'topicid': topic.topicid,
                    'topicname': topic.topicname,
                    'layers': topic.layers,
                    'authority': {
                        'authorityuuid': topic.authority.authorityid,
                        'authorityname': topic.authority.authorityname,
                        'authorityurl': topic.authority.authoritywww
                        },
                    'topicorder': topic.topicorder,
                    'authorityfk': topic.authorityfk,
                    'publicationdate': topic.publicationdate,
                    'restrictions': [],
                    'legalbases': legalbases,
                    'legalprovisions': legalprovisions,
                    'hints': hints,
                    'topiclegend': completelegend,
                    'bboxlegend': [],
                    'wmslayerlist': wmslayerlist
                    }

            return topics
        else:
            raise HTTPBadRequest('No topic was found.')

    def set_topic_map(self, request):
        """
        """

        bbox = self.real_estate['BBOX']

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
        wms_base_layers = request.registry.settings['app_config']['crdppf_wms_layers']
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

        for topic in self.topics:
            topiclayers = {
                "baseURL": request.registry.settings['crdppf_wms'],
                "opacity": 1,
                "type": "WMS",
                "layers": self.topiclist[topic.topicorder]['wmslayerlist'],
                "imageFormat": "image/png",
                "styles": "default",
                "customParams": {
                    "TRANSPARENT": "true"
                }
            }

            map = {
                "projection": "EPSG:"+str(self.srid),
                "dpi": 150,
                "rotation": 0,
                "center": [self.real_estate['centerX'],self.real_estate['centerY']],
                "scale": self.print_box['scale']*self.appconfig['map_buffer'],
                "longitudeFirst": "true",
                "layers": [
                    {
                        "type": "geojson",
                        "geoJson": request.route_url('get_property')+'?id='+self.propertyid,
                        "style": {
                            "version": "2",
                            "strokeColor": "gray",
                            "strokeLinecap": "round",
                            "strokeOpacity": 0.5,
                            "[INTERSECTS(geometry, "+wkt_polygon+")]": {
                                "symbolizers": [
                                    {
                                        "strokeColor": "red",
                                        "strokeWidth": 4,
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
            self.topiclist[topic.topicorder].update({'map': map})

        return map

    def get_layers(self):
        """ Get the list of all PLR layers
        """

        layers = DBSession.query(Layers).filter(Layers.baselayer.is_(False)).order_by(Layers.layerid).all()
        if len(layers) > 0:
            layerlist = []
            for layer in layers:
                layerlist.append({
                    'layerid': layer.layerid,
                    'topicid': layer.topicfk,
                    'topicorder': layer.topic.topicorder,
                    'layername': layer.layername,
                    'publicationdate': layer.publicationdate
                })

        return layers

    def get_restrictions(self):
        """ For each available topic, get the restrictions
        """

        parcelGeom = self.real_estate['geom']

        if len(self.layers) > 0:
            restrictionlist = []

            for layer in self.layers:
                results = get_features_function(parcelGeom, {'layerList': layer.layername})

                if len(results) > 0:
                    codegenre = None
                    groupedrestriction = {}

                    for result in results:
                        # make sure, all type codes are cast to string
                        if isinstance(result['properties']['codegenre'], int):
                            result['properties']['codegenre'] = str(result['properties']['codegenre'])
                        # remove all text formatting for area calculation
                        if result['properties']['intersectionMeasure'] == ' ':
                            measure = 1
                        else:
                            measure = int(result['properties']['intersectionMeasure'].replace(' : ', '').replace(' - ', '').replace('[m2]', '').replace('[m]', ''))

                        restriction = {
                            'topicorder': layer.topic.topicorder,
                            'topicid': layer.topic.topicid,
                            'topicname': layer.topic.topicname,
                            'layername': layer.layername,
                            'restrictionid': result['id'],
                            'teneur': result['properties']['teneur'],
                            'codegenre': result['properties']['codegenre'],
                            'statutjuridique': result['properties']['statutjuridique'],
                            'datepublication': result['properties']['datepublication'],
                            'intersectionMeasure': measure,
                            'geomType': result['properties']['geomType']
                        }

                        # a restrictioin must have a type code set
                        if restriction['codegenre'] is None:
                            raise HTTPBadRequest('At least one restriction returned an empty type code.')

                        # compile the restrictions list and push it back to the topiclist
                        restrictionlist.append(restriction)

                        propertyarea = self.real_estate['area']
                        if isinstance(restriction['codegenre'], int):
                            restriction['codegenre'] = str(restriction['codegenre'])

                        if codegenre == result['properties']['codegenre']:
                            groupedmeasure =+ measure
                            groupedrestriction[codegenre]['area'] = groupedmeasure
                        else:
                            codegenre = result['properties']['codegenre']
                            groupedmeasure = measure
                            groupedrestriction[codegenre] = {
                                "codegenre": self.legenddir+result['properties']['codegenre']+".png",
                                "teneur": result['properties']['teneur'],
                                "geomType": result['properties']['geomType'],
                                "area": groupedmeasure
                            }

                    for code in groupedrestriction:
                        if groupedrestriction[code]['geomType'] == 'area':
                            self.topiclist[layer.topic.topicorder]['restrictions'].append({
                                "codegenre": groupedrestriction[code]['codegenre'],
                                "teneur": groupedrestriction[code]['teneur'],
                                "area": str(groupedrestriction[code]['area'])+' m<sup>2</sup>',
                                "area_pct": round((float(
                                    groupedrestriction[code]['area'])*100)/propertyarea, 1)
                            })
                        elif groupedrestriction[code]['geomType'] == 'point':
                            self.topiclist[layer.topic.topicorder]['restrictions'].append({
                                "codegenre": groupedrestriction[code]['codegenre'],
                                "teneur": groupedrestriction[code]['teneur'],
                                "area": str(groupedrestriction[code]['area']),
                                "area_pct": -1
                            })
                        else:
                            self.topiclist[layer.topic.topicorder]['restrictions'].append({
                                "codegenre": groupedrestriction[code]['codegenre'],
                                "teneur": groupedrestriction[code]['teneur'],
                                "area": str(groupedrestriction[code]['area'])+ ' m',
                                "area_pct": -1
                            })

                del(results)
        else:
            raise HTTPBadRequest('No layer with restrictions found.')

        return restrictionlist

    def get_references(self):
        """ For each restriction get the references
        """
        if len(self.restrictions) > 0:
            for restriction in self.restrictions:
                references = DBSession.query(OriginReference).filter(
                    OriginReference.fkobj==restriction['restrictionid']
                    ).order_by(OriginReference.docid).all()

                if len(references) > 0:
                    legalbases = []
                    legalprovisions = []
                    hints = []

                    docidlist = set()
                    for reference in references:

                        if reference.docid in docidlist:
                            pass
                        else:
                            docidlist.add(reference.docid)
                        if restriction['topicid'] in self.docids.keys():
                            self.docids[restriction['topicid']].update(docidlist)
                        else:
                            self.docids.update({restriction['topicid']: docidlist})

            for topic in self.topics:
                if topic.topicid in self.docids.keys():
                    references = DBSession.query(LegalDocuments).filter(
                        LegalDocuments.docid.in_(self.docids[topic.topicid])
                        ).order_by(LegalDocuments.doctype
                        ).order_by(LegalDocuments.state.desc()
                        ).order_by(LegalDocuments.officialnb).all()

                    for reference in references:
                        if reference.abbreviation is None:
                             reference.abbreviation = ''
                        if reference.officialnb is None:
                             reference.officialnb = ''
                        if reference.doctypes.value == 'legalbase':
                            self.topiclist[topic.topicorder]['legalbases'].append({
                                'docid': reference.docid,
                                'doctype': reference.doctypes.value,
                                'officialtitle': reference.officialtitle,
                                'title': reference.title,
                                'officialnb': reference.officialnb,
                                'abbreviation': reference.abbreviation,
                                'remoteurl': reference.remoteurl
                            })
                        elif reference.doctypes.value == 'legalprovision':
                            self.topiclist[topic.topicorder]['legalprovisions'].append({
                                'docid': reference.docid,
                                'doctype': reference.doctypes.value,
                                'officialtitle': reference.officialtitle,
                                'title': reference.title,
                                'officialnb': reference.officialnb,
                                'abbreviation': reference.abbreviation,
                                'remoteurl': reference.remoteurl
                            })
                        else:
                            self.topiclist[topic.topicorder]['hints'].append({
                                'docid': reference.docid,
                                'doctype': reference.doctypes.value,
                                'title': reference.title,
                                'abbreviation': reference.abbreviation,
                                'officialtitle': reference.officialtitle,
                                'officialnb': reference.officialnb,
                                'remoteurl': reference.remoteurl
                            })

        return

    def set_topic_categorie(self):
        """ Attribut all topics to one of the categories
        """

        for topic in self.topics:

            if str(topic.topicid) in self.appconfig['emptytopics']:
                self.emptytopics.append(topic.topicname)
            else:
                if len(self.topiclist[topic.topicorder]['restrictions']) > 0:
                    self.topiclist[topic.topicorder]['categorie'] = 3
                    self.concernedtopics.append({
                        'topicname': topic.topicname,
                        'documentlist': {
                            "columns": [
                                "appendixno",
                                "appendixtitle"
                            ],
                            "data": []
                            }
                    })
                else:
                    self.topiclist[topic.topicorder]['categorie'] = 1
                    self.notconcernedtopics.append(topic.topicname)
        return


    def set_print_format(self, request):
        """ Gets the parameters of the page layout and calculates the WMS box
            needed for printing
        """

        bbox = self.real_estate['BBOX']
        fitratio = self.pdfconfig['fitratio']
        print_format = get_print_format(bbox, fitratio)

        return print_format


    def set_mapbox(self):
        """Function to calculate the coordinates of the map bounding box in the real world
            height: map height in mm
            width: map width in mm
            scale: the map scale denominator
            feature_center: center point (X/Y) of the real estate feature
        """
        scale = self.print_box['scale']
        height = self.print_box['height']
        width = self.print_box['width']
        buffer = self.appconfig['map_buffer']

        scale = scale*buffer
        delta_Y = round((height*scale/1000)/2, 1)
        delta_X = round((width*scale/1000)/2, 1)
        X = round(self.real_estate['centerX'],1)
        Y = round(self.real_estate['centerY'], 1)

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

        self.basemap['map_bbox'] = map_bbox


    def fetch_bbox_legend(self, request):
        """get the legend entries in the map bbox not touching the features
        """

        for layer in self.layers:

            featurelegend = get_legend_classes(to_shape(self.real_estate['geom']), layer.layername, self.translations, self.srid)
            bboxlegend = get_legend_classes(to_shape(WKTElement(self.basemap['map_bbox'])), layer.layername, self.translations, self.srid)
            bboxitems = set()

            for legenditem in bboxlegend:
                if legenditem not in featurelegend:
                    bboxitems.add(tuple(legenditem.items()))
            if len(bboxitems) > 0:
                for el in bboxitems:
                    legendclass = dict((x, y) for x, y in el)
                    legendclass['codegenre'] = self.legenddir+legendclass['codegenre']+".png"
                    self.topiclist[layer.topic.topicorder]['bboxlegend'].append(legendclass)
