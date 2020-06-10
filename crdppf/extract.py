# -*- coding: utf-8 -*-
from crdppf import db_config

from pyramid.httpexceptions import HTTPBadRequest, HTTPNotFound
from datetime import datetime

from crdppf.util.pdf_functions import get_translations, get_feature_info

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
