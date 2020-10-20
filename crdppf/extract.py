# -*- coding: UTF-8 -*-
from sqlalchemy import or_

from crdppf import db_config

from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from datetime import datetime

from crdppfportal.table2model_match import table2model_match

from crdppf.util.pdf_functions import get_translations, get_feature_info
from crdppf.util.get_feature_functions import get_features_function

from crdppf.models import DBSession
from crdppf.models.models import Topics, Layers, OriginReference

# MAIN DOCUMENT
class Extract(object):
    """The main class for the ectract object which collects all the data to write the report."""

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
        # parameters for the header
        self.header = {}
        # parameters for the footer
        self.footer = {}
        # array with specific data for the titlepage
        self.titlepage = {}
        # array holding the values for the table of content (toc)
        self.tocpage = {}
        # array containing the content of the topicpages
        self.topicpages = {}
        # array with the data of all appendices
        self.appendices = {}
        # array with list of the concerned documents
        self.doclist = []
        # dict used to store the entries of the table of content
        self.toc_entries = {}
        # dict to store the values of the appendix list
        self.appendix_entries = []
        # dict to store the refernces data
        self.reference_entries = []
        self.appendix_links = []
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

        #Ttry:
        self.topics = self.get_topics()
        #except:
        #    raise HTTPNotFound('There is an error regarding the topics for this municipality.')

        #try:
        self.layers = self.get_layers()
        #except:
        #    raise HTTPNotFound('An error occured fetching the PLR relevant layers.')

        self.restrictions = self.get_restrictions()

        self.references = self.get_references()


    def get_topics(self):
        """ Get the list of PLR topics
        """

        topics = DBSession.query(Topics).order_by(Topics.topicorder).all()
        if len(topics) > 0:
            topiclist = {}
            for topic in topics:
                topiclist[topic.topicorder] = {
                    'topicid': topic.topicid,
                    'topicname': topic.topicname,
                    'publicationdate': topic.publicationdate,
                    'authority': topic.authority,
                    'layers': topic.layers
                }
        else:
            raise HTTPBadRequest('No topic was found.')

        return topiclist

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
                    for result in results:
                        restriction = {
                            'topicid': layer.topic.topicid,
                            'topicname': layer.topic.topicname,
                            'layername': layer.layername,
                            'restrictionid': result['id'],
                            'teneur': result['properties']['teneur'],
                            'codegenre': result['properties']['codegenre'],
                            'statutjuridique': result['properties']['statutjuridique'],
                            'datepublication': result['properties']['datepublication'],
                            'intersectionMeasure': result['properties']['intersectionMeasure'],
                            'geomType': result['properties']['geomType']
                        }
                        restrictionlist.append(restriction)
                del(results)
        else:
            raise HTTPBadRequest('No layer found for this restriction.')

        return restrictionlist

    def get_references(self):
        """ For each restriction get the references
        """
        if len(self.restrictions) > 0:
            for restriction in self.restrictions:
                references = DBSession.query(OriginReference).filter(OriginReference.fkobj==restriction['restrictionid']).order_by(OriginReference.docid).all()

                if len(references) > 0:
                    referencelist = []
                    for reference in references:
                        referencelist.append({
                            'docid': reference.docid,
                            'officialtitle': reference.documents.officialtitle,
                            'officialnb': reference.documents.officialnb,
                            'remoteurl': reference.documents.remoteurl
                        })
                restriction.update({'references': referencelist})

            sdf

        return referencelist
