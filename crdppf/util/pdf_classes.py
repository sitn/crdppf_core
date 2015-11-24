# -*- coding: UTF-8 -*-

from os import remove

from fpdf import FPDF
import pkg_resources
from datetime import datetime

from PIL import Image
from StringIO import StringIO

from geoalchemy2 import WKTElement

import httplib2
from urlparse import urlparse

from xml.dom.minidom import parseString

from crdppf.models import DBSession
from crdppf.models import AppConfig

from crdppf.views.get_features import get_features_function
from crdppf.views.legal_documents import getLegalDocuments
from crdppf.views.legal_documents import getDocumentReferences
from crdppf.util.pdf_functions import geom_from_coordinates

class AppConfig(object):
    """Class holding the definition of the basic parameters loaded from yaml
    """
    def __init__(self, config):
        # tempdir : Path to the working directory where the temporary files will be stored
        try:
            self.tempdir = config['tempdir']
        except:
            self.tempdir = pkg_resources.resource_filename('crdppfportal', 'static/public/temp_files/')
        try:
            self.slddir = config['slddir']
        except:
            self.slddir = pkg_resources.resource_filename('crdppfportal', 'static/public/') 
        # pdfbasedir : Path to the directory where the generated pdf's will be stored
        self.pdfbasedir = pkg_resources.resource_filename('crdppfportal', 'static/public/pdf/') 
        # imagesbasedir : Path to the directory where the images resources are stored
        self.imagesbasedir = pkg_resources.resource_filename('crdppfportal','static/images/')
        # municipalitylogodir : Path to the directory where the logos of the municipalities are stored
        self.municipalitylogodir = pkg_resources.resource_filename('crdppfportal','static/images/ecussons/')
        # legaldocsdir : Path to the folder where the legal documents are stored that may or may not be included
        try:
            self.legaldocsdir  = config['legaldocsdir']
        except:
            self.legaldocsdir = pkg_resources.resource_filename('crdppfportal', 'static/public/reglements/') 
        self.ch_wms_layers = []
        # ch_topics : Restrictions on federal level
        self.ch_topics = config['ch_topics']
        # ch_legend_layers: Mapping between internal layer name and layer name used for the feature and web service call
        self.ch_legend_layers = config['ch_legend_layers']
        self.crdppf_wms_layers = config['crdppf_wms_layers']
        self.wms_srs = config['wms_srs']
        self.wms_version = config['wms_version']
        self.wms_transparency = config['wms_transparency']
        self.wms_imageformat = config['wms_imageformat']
        self.emptytopics = config['emptytopics']
        try: 
            self.doctypes = config['doctypes'].split(',')
        except:
            self.doctypes = 'legalbase,legalprovision,reference,temporaryprovision,map,other'.split(',')

class PDFConfig(object):
    """A class to define the configuration of the PDF extract to simplify changes.
    """
    def __init__(self, config):
    # PDF Configuration
        self.defaultlanguage = config['defaultlanguage'].lower()
        # default size of the PDF document A4, A3, A2, A1 - fixed by the pilot project to A4
        self.pdfformat = config['pdfformat']
        # default orientation of the PDF document - fixed to portrait by the group
        self.pdforientation = config['pdforientation']
        # left margin of the PDF's content block
        self.leftmargin = config['leftmargin']
        self.rightmargin = config['rightmargin']
        self.topmargin = config['topmargin']
        self.headermargin = config['headermargin']
        self.footermargin = config['footermargin']
        # Grouped margin values for an easy access
        self.pdfmargins = [
            self.leftmargin,
            self.topmargin,
            self.rightmargin
        ]
        self.fontfamily = config['fontfamily']
        self.textstyles = config['textstyles']
        for style_key in self.textstyles:
            if self.textstyles[style_key][0] == 'N':
                self.textstyles[style_key][0] = ''
            if len(self.textstyles[style_key]) < 3:
                self.textstyles[style_key].insert(0, self.fontfamily)
        
        self.urlcolor = config['urlcolor']
        self.defaultcolor = config['defaultcolor']
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        self.siteplanname = str(self.timestamp)+'_siteplan'
        self.fitratio = config['fitratio']
        self.pdfpath = pkg_resources.resource_filename('crdppfportal', 'static/public/pdf/')
        # CHlogopath : Path to the header logo of the Swiss Confederation
        self.CHlogopath = config['CHlogopath']
        # cantonlogopath : Path to the header logo of the canton
        self.cantonlogopath = config['cantonlogo']['path']
        self.cantonlogoheight = config['cantonlogo']['height']
        self.cantonlogowidth = config['cantonlogo']['width']
        self.placeholder = config['placeholder']
        self.pdfbasename = config['pdfbasename']
        self.siteplanbasename = config['siteplanbasename']
        self.optionaltopics = config['optionaltopics']
        try:
            self.pilotphase  = config['pilotphase']
        except:
            self.pilotphase = False
        try:
            self.disclaimer  = config['disclaimer']
        except:
            self.disclaimer = False
        try:
            self.signature  = config['signature']
        except:
            self.signature = False 

class AppendixFile(FPDF):
    """The helper class to create the appendices files with the same corporate
    design and attach them to the main document if needed"""
    
    def __init__(self):
        FPDF.__init__(self)
        self.pdfconfig = {}
        
    def load_app_config(self, config):
        """Initialises the basic parameters of the application, like the language or the working
        directories. For details look also at the AppConfig class.
        """
        self.appconfig = AppConfig(config)

    def set_pdf_config(self, config):
        """Loads the initial configuration of the PDF page, like the format, orientation, styles and so on.
        for details look at the PDFConfig class.
        """
        self.pdfconfig = PDFConfig(config)

    def header(self):
        """Creates the document header with the logos and vertical lines."""

        # Add the vertical lines
        self.set_line_width(0.3)
        self.line(105, 0, 105, 35)
        self.line(165, 0, 165, 35)
        # Add the logos if existing else put a placeholder
        self.image(self.appconfig.imagesbasedir+self.pdfconfig.CHlogopath, 10, 8, 55, 14.42)
        self.image(self.appconfig.imagesbasedir+self.pdfconfig.cantonlogopath, 110, 8, self.pdfconfig.cantonlogowidth, self.pdfconfig.cantonlogoheight)
        try:
            self.image(self.municipalitylogopath, 170, 8, 10, 10.7)
        except:
            self.image(self.appconfig.municipalitylogodir+self.pdfconfig.placeholder, 170, 8, 10, 10.7)

        # This lines are not necessary if the community name is already contained in the picture
        self.set_xy(170, 19.5)
        self.set_font(*self.pdfconfig.textstyles['small'])
        self.cell(30, 3, self.municipality.encode('iso-8859-1'), 0, 0, 'L')

    def footer(self):
        """Creates the document footer"""

        # position footer at 15mm from the bottom
        self.set_y(-20)
        self.set_font(*self.pdfconfig.textstyles['small'])
        self.set_text_color(*self.pdfconfig.defaultcolor)
        self.cell(55, 5, self.translations['creationdatelabel']+str(' ')+self.creationdate, 0, 0, 'L')
        if self.reporttype == 'certified' or self.reporttype == 'reducedcertified':
            self.cell(60, 5, self.translations['signaturelabel']+str(' ')+self.timestamp, 0, 0, 'C')
        else:
            self.cell(60, 5, self.translations['nosignaturetext'], 0, 0, 'C')
        self.cell(55, 5, str(self.current_page), 0, 0, 'R')


# MAIN DOCUMENT
class Extract(FPDF):
    """The main class for the ectract object which collects all the data, then writes the pdf report."""
    # HINTS #
    # to get vars defined in the buildout  use : request.registry.settings['key']
    
    def __init__(self, request, log):
        # loading the PDF library
        FPDF.__init__(self)
        # assigning the request variables
        self.request = request
        # fetch the base URL for the local WMS calls
        self.crdppf_wms = request.registry.settings['crdppf_wms']
        # fetching the base URL for the remote WMS calls (confederation)
        self.ch_wms = request.registry.settings['ch_wms']
        # fetching the base URL for the confederation's feature service
        self.chfs_baseurl = request.registry.settings['chfs_baseurl']
        # gets the local path to the working directory for temporary files
        self.sld_url = request.static_url('crdppfportal:static/public/temp_files/')
        # gets the path of the folter with the legend files
        self.topiclegenddir = request.static_url('crdppfportal:static/public/legend/')
        # sets the creation date of the PDF instance
        self.creationdate = datetime.now().strftime("%d.%m.%Y-%H:%M:%S")
        # same same but different use
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        # initializes an empty array for the calculated pdf/print configuration paraameters
        self.printformat = {}
        # empty array for all the dynamic wms parameters like the bbox, center coords
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
        # setting the default  root filename of the PDF and temporary files
        self.filename = 'thefilename'
        # empty dict for a list of  the topics and it's depending values
        self.topiclist = {}
        self.layerlist = {}
        self.legalbaselist = {}
        self.legalprovisionslist = {}
        self.referenceslist = {}
        self.doclist = []
        # dict used to store the entries of the table of content
        self.toc_entries = {}
        # dict to store the values of the appendix list
        self.appendix_entries = []
        # dict to store the refernces data
        self.reference_entries = []
        self.appendix_links = []
        self.topicorder = {}
        self.wms_baselayers = []
        self.log = log
        self.cleanupfiles = []
        self.basemap = ''

    def alias_no_page(self, alias='{no_pg}'):
        """Define an alias for total number of pages"""
        self.str_alias_no_page = alias
        return alias
        
    def load_app_config(self, config):
        """Initialises the basic parameters of the application.
        """
        self.appconfig = AppConfig(config)
        self.doctypes = self.appconfig.doctypes

    def set_pdf_config(self, config):
        """Loads the initial configuration of the PDF page.
        """
        self.pdfconfig = PDFConfig(config)

    def set_filename(self):
        """ Sets the file name of the pdf extract based on the time and parcel id
        """
        self.filename = str(self.timestamp) + self.featureid
        self.pdfconfig.pdfname = str(self.filename) + self.pdfconfig.pdfbasename
        self.pdfconfig.siteplanname = str(self.filename) + self.pdfconfig.siteplanbasename

    def header(self):
        """Creates the document header with the logos and vertical lines."""

        # Add the vertical lines
        self.set_line_width(0.3)
        self.line(105, 0, 105, 35)
        self.line(165, 0, 165, 35)
        # Add the logos if existing else put a placeholder
        # to put ch-logo dimensions in variable
        self.image(self.appconfig.imagesbasedir+self.pdfconfig.CHlogopath, 10, 8, 55, 14.42)
        self.image(self.appconfig.imagesbasedir+self.pdfconfig.cantonlogopath, 110, 8, self.pdfconfig.cantonlogowidth, self.pdfconfig.cantonlogoheight)
        try:
            self.image(self.municipalitylogopath, 170, 8, 10, 10.7)
        except:
            self.image(self.appconfig.municipalitylogodir+self.pdfconfig.placeholder, 170, 8, 10, 10.7)
        # This lines are not necessary if the community name is already contained in the picture
        self.set_xy(170, 19.5)
        self.set_font(*self.pdfconfig.textstyles['small'])
        self.cell(30, 3, self.municipality.encode('iso-8859-1'), 0, 0, 'L')

        # Once the header has been placed at the right place, we re-initialize y for text placing
        self.set_y(self.t_margin)

    def footer(self):
        """Creates the document footer"""

        # position footer at 15mm from the bottom
        self.set_y(-20)
        self.set_font(*self.pdfconfig.textstyles['small'])
        self.set_text_color(*self.pdfconfig.defaultcolor)
        self.cell(55, 5, self.translations['creationdatelabel']+str(' ')+self.creationdate, 0, 0, 'L')
        if self.reportInfo['type'] == 'certified' or self.reportInfo['type'] == 'reducedcertified':
            self.cell(60, 5, self.translations['signaturelabel']+str(' ')+self.timestamp, 0, 0, 'C')
        else:
            self.cell(60, 5, self.translations['nosignaturetext'], 0, 0, 'C')
        self.cell(55, 5, self.translations['pagelabel']+str(' ')+str(self.page)+str('/')+ \
                str(self.alias_nb_pages()), 0, 0, 'R')

    def set_wms_config(self, topicid):
        """ Sets the basic WMS parameters in function of the topic
        """
        self.ch_topics = self.appconfig.ch_topics
        self.wms_srs = self.appconfig.wms_srs
        self.wms_version = self.appconfig.wms_version
        self.wms_transparency = self.appconfig.wms_transparency
        self.wms_params = {
            'SERVICE': 'WMS',
            'VERSION': str(self.wms_version) ,
            'SRS': str(self.wms_srs),
            'lang':self.lang
            }
        for key, value in self.wms_params.iteritems():
            self.wms_get_legend[key] = value
            self.wms_get_styles[key] = value
        if topicid in self.ch_topics:
            self.wms_url = self.ch_wms
        else:
            self.wms_url = self.crdppf_wms

    # gets the basemap to display the selected property  in the cadastral context
    def get_basemap(self):
        # defines the corrners and the center point of the bbox for the wms call of the map
        wmsBBOX, wmsbbox = self.get_wms_bbox()

        params = {
            'REQUEST': 'GetMap',
            'VERSION': self.appconfig.wms_version,
            'LAYERS': ",".join(self.appconfig.crdppf_wms_layers),
            'SRS': self.appconfig.wms_srs,
            'BBOX': ",".join([str(wmsBBOX['minX']), str(wmsBBOX['minY']), str(wmsBBOX['maxX']), str(wmsBBOX['maxY'])]),
            'WIDTH': self.mapconfig['width'],
            'HEIGHT': self.mapconfig['height'],
            'FORMAT': 'image/png',
            'TRANSPARENT': 'false'
        }

        getmapurl = self.crdppf_wms

        if getmapurl.find('?') < 0:
            getmapurl += '?'
        getmapurl = getmapurl + '&'.join(['%s=%s' % (key, value) for (key, value) in params.items()])

        http = httplib2.Http()

        h = dict(self.request.headers)
        if urlparse(getmapurl).hostname != 'localhost': 
            h.pop('Host')

        try:
            resp, content = http.request(getmapurl, method='GET', headers=h)
        except: 
            self.log.error("Unable to do GetMap request for url %s" % getmapurl)
            return None

        self.basemap = Image.open(StringIO(content))
        
    def get_title_page(self):
        """Creates the title page of the PDF extract with the summary and a situation map of the property.
        """
        today= datetime.now()

        # START TITLEPAGE
        self.add_page()
        self.set_font(*self.pdfconfig.textstyles['title1'])
        self.set_margins(*self.pdfconfig.pdfmargins)

        # following 3 lines to replace - used for convenience only
        translations = self.translations
        pdfconfig = self.pdfconfig
        feature_info = self.featureInfo

        # PageTitle
        self.set_y(45)
        self.set_font(*self.pdfconfig.textstyles['title1'])
        # write document title in function of the selected extract type
        if self.reportInfo['type'] =='certified':
            self.multi_cell(0, 9, self.translations["certifiedextracttitlelabel"])
        elif self.reportInfo['type'] =='reduced':
            self.multi_cell(0, 9, self.translations['reducedextracttitlelabel'])
        elif self.reportInfo['type'] =='reducedcertified':
            self.multi_cell(0, 9, self.translations['reducedcertifiedextracttitlelabel'])
        else:
            self.reportInfo['type'] = 'standard'
            self.multi_cell(0, 9, self.translations['normalextracttitlelabel'])
        self.set_font(*self.pdfconfig.textstyles['title2'])
        self.multi_cell(0, 7, self.translations['extractsubtitlelabel'])
        self.ln()

        # placing the map - mapsize to put in variable
        map = self.image(self.sitemappath, 25, 80, 160, 90)

        y=self.get_y()
        # rectangle size to put in variable
        self.rect(25, 80, 160, 90, '')
        self.set_y(y+105)

        # First infoline
        self.set_font(*self.pdfconfig.textstyles['bold'])
        self.cell(45, 5, self.translations['propertylabel'], 0, 0, 'L')

        self.set_font(*self.pdfconfig.textstyles['normal'])
        # should we generalize the dict keys like 'nomcad'?
        if 'nomcad' in feature_info:
            if feature_info['nomcad'] and feature_info['type']:
                self.cell(50, 5, feature_info['nummai'].encode('iso-8859-1')+str(' (')+ \
                    feature_info['nomcad'].encode('iso-8859-1')+str(') ')+ \
                    str(' - ')+feature_info['type'].encode('iso-8859-1'), 0, 1, 'L')
            else:
                self.cell(50, 5, feature_info['nummai'].encode('iso-8859-1'), 0, 1, 'L')
        else:
            if feature_info['nomcom'] is not None:
                self.cell(50, 5, feature_info['nummai'].encode('iso-8859-1')+ \
                    str(' ')+str(' - ')+feature_info['type'].encode('iso-8859-1'), 0, 1, 'L')
            else:
                self.cell(50, 5, feature_info['nummai'].encode('iso-8859-1'), 0, 1, 'L')

         # Second infoline : Area and EGRID
        self.set_font(*pdfconfig.textstyles['bold'])
        self.cell(45, 5, translations['propertyarealabel'], 0, 0, 'L')
        self.set_font(*pdfconfig.textstyles['normal'])
        self.cell(50, 5, str(feature_info['area'])+str(' m2').encode('iso-8859-1'), 0, 0, 'L')
        self.set_font(*pdfconfig.textstyles['bold'])
        self.cell(35, 5, translations['EGRIDlabel'], 0, 0, 'L')
        self.set_font(*pdfconfig.textstyles['normal'])
        self.cell(50, 5, feature_info['no_egrid'].encode('iso-8859-1'), 0, 1, 'L')

        # Third infoline : Adresse/localisation
        self.set_font(*pdfconfig.textstyles['bold'])
        self.cell(45, 5, translations['addresslabel'], 0, 0, 'L')
        self.set_font(*pdfconfig.textstyles['normal'])
        if 'adresse' in feature_info:
            self.cell(50, 5, feature_info['adresse'].encode('iso-8859-1'), 0, 1, 'L')
        else: 
            self.cell(50, 5, self.translations['noaddresstext'], 0, 1, 'L')

         # Fourth infoline : municipality and BFS number
        self.set_font(*pdfconfig.textstyles['bold'])
        self.cell(45, 5,  translations['municipalitylabel']+str(' (')+translations['federalmunicipalitynumberlabel']+str(')'), 0, 0, 'L')
        self.set_font(*pdfconfig.textstyles['normal'])
        self.cell(50, 5, feature_info['nomcom'].encode('iso-8859-1')+str(' (')+str(feature_info['nufeco']).encode('iso-8859-1')+str(')'), 0, 0, 'L')

        # Creation date and operator
        y= self.get_y()
        self.set_y(y+10)
        self.set_font(*pdfconfig.textstyles['bold'])
        self.cell(45, 5, translations['extractoperatorlabel'], 0, 0, 'L')
        self.set_font(*pdfconfig.textstyles['normal'])
        self.cell(70, 5, feature_info['operator'].encode('iso-8859-1'), 0, 1, 'L')

        # == this note is published only as long as the legal documents are not validated
        # Pilot phase information block - to de/activate in config_pdf.yaml.in
        if pdfconfig.pilotphase == True :
            y= self.get_y()
            self.set_y(y+5)
            self.set_font(*pdfconfig.textstyles['bold'])
            self.multi_cell(0, 5, translations['pilotphasetxt'], 0, 1, 'L')
        # == end of temporary info will be removed and original code :

        # Signature block for certified extracts - to de/activate in config_pdf.yaml.in
        if pdfconfig.signature == True :
            if self.reportInfo['type'] == 'certified' or self.reportInfo['type'] == 'reducedcertified':
                y= self.get_y()
                self.set_y(y+5)
                self.set_font(*pdfconfig.textstyles['bold'])
                self.cell(0, 5, translations['signaturelabel']+str(' ')+self.timestamp, 0, 0, 'L')

        # Disclaimer block - to de/activate in config_pdf.yaml.in
        if pdfconfig.disclaimer == True :
            self.set_y(250)
            self.set_font(*pdfconfig.textstyles['bold'])
            self.cell(0, 5, translations['disclaimerlabel'], 0, 1, 'L')
            self.set_font(*pdfconfig.textstyles['normal'])
            self.multi_cell(0, 5, translations['disclaimer'], 0, 1, 'L')

        # END TITLEPAGE

    def get_map_format(self):
        """ Function to define the center and the bounding box of the map request to the wms
        """
        self.mapconfig = {'width':self.printformat['mapWidth'], 'height':self.printformat['mapHeight']}
        self.mapconfig['bboxCenterX'] = (self.featureInfo['BBOX']['maxX']+self.featureInfo['BBOX']['minX'])/2
        self.mapconfig['bboxCenterY'] = (self.featureInfo['BBOX']['maxY']+self.featureInfo['BBOX']['minY'])/2

    def get_legend_classes(self, bbox, layername):
        """ Collects all the features in the map perimeter into a list to create a dynamic legend
        """
        geom = geom_from_coordinates(bbox)
        # transform coordinates from wkt to SpatialElement for intersection
        polygon = WKTElement(geom.wkt, 21781)
        mapfeatures = get_features_function(polygon, {'layerList':layername, 'translations':self.translations})
        if mapfeatures is not None:
            classes = []
            for mapfeature in mapfeatures:
                classes.append(str(mapfeature['properties']['codegenre']))

        return classes

    def get_site_map(self):
        """Creates the situation map of the property.
           input : the property's id,
           output : mapimage, mappath
        """

        # Create property highlight sld
        sld = u"""<?xml version="1.0" encoding="UTF-8"?>
        <sld:StyledLayerDescriptor version="1.0.0" xmlns="http://www.opengis.net/ogc" xmlns:sld="http://www.opengis.net/sld" xmlns:ogc="http://www.opengis.net/ogc" xmlns:gml="http://www.opengis.net/gml" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.opengis.net/sld http://schemas.opengis.net/sld/1.0.0/StyledLayerDescriptor.xsd">
        <sld:NamedLayer>
        <sld:Name>parcelles</sld:Name>
        <sld:UserStyle>
        <sld:Name>propertyIsEqualTo</sld:Name>
        <sld:Title>propertyIsEqualTo</sld:Title>
        <sld:FeatureTypeStyle>
        <sld:Rule>
        <ogc:Filter>
        <ogc:PropertyIsEqualTo>
        <ogc:PropertyName>idemai</ogc:PropertyName>
        <ogc:Literal>"""
        sld += str(self.featureid)
        sld += u"""</ogc:Literal>
        </ogc:PropertyIsEqualTo>
        </ogc:Filter>
        <sld:PolygonSymbolizer>
        <sld:Stroke>
        <sld:CssParameter name="stroke">#ff0000</sld:CssParameter>
        <sld:CssParameter name="stroke-opacity">1</sld:CssParameter>
        <sld:CssParameter name="stroke-width">5</sld:CssParameter>
        </sld:Stroke>
        </sld:PolygonSymbolizer>
        <sld:TextSymbolizer>
        <sld:Label>
        <ogc:PropertyName>nummai</ogc:PropertyName>
        </sld:Label> 
        <sld:Font>
        <sld:CssParameter name="font-family">"""
        sld += self.pdfconfig.fontfamily
        sld += """</sld:CssParameter> 
        <sld:CssParameter name="font-weight">bold</sld:CssParameter> 
        <sld:CssParameter name="font-size">16</sld:CssParameter> 
        </sld:Font>
        <sld:Fill>
        <sld:CssParameter name="fill">#000000</sld:CssParameter> 
        </sld:Fill>
        <sld:Halo>
        <sld:Radius>3</sld:Radius>
        <sld:Fill><sld:CssParameter name="fill">#FFFFFF</sld:CssParameter></sld:Fill>
        </sld:Halo>
        </sld:TextSymbolizer>
        </sld:Rule>
        </sld:FeatureTypeStyle>
        </sld:UserStyle>
        </sld:NamedLayer>
        </sld:StyledLayerDescriptor>"""

        sldfile = open(self.appconfig.tempdir+self.pdfconfig.siteplanname+'_sld.xml', 'w')
        self.cleanupfiles.append(self.appconfig.tempdir+self.pdfconfig.siteplanname+'_sld.xml')
        sldfile.write(sld)
        sldfile.close()

        # Layers as defined in our WMS - to replace with an array from a table
        layers = self.appconfig.crdppf_wms_layers

        scale = self.printformat['scale']*2
        # SitePlan/Plan de situation/Situationsplan
        # first we set the pdf's map canavas dimensions in cm
        sitemapparams = {'width':self.printformat['mapWidth'],'height':self.printformat['mapHeight']}
        # then the center coordinates of the bbox are determined based on the feature's bbox
        sitemapparams['bboxCenterX'] = (self.featureInfo['BBOX']['maxX']+self.featureInfo['BBOX']['minX'])/2
        sitemapparams['bboxCenterY'] = (self.featureInfo['BBOX']['maxY']+self.featureInfo['BBOX']['minY'])/2
        #to recenter the map on the bbox of the feature, with the right scale and add at least 10% of space we calculate a wmsBBOX
        wmsBBOX = {}
        wmsBBOX['centerY'] =  int(sitemapparams['bboxCenterY'])
        wmsBBOX['centerX'] =  int(sitemapparams['bboxCenterX'])
        wmsBBOX['minX'] = int(wmsBBOX['centerX'] - (160*scale/1000/2))
        wmsBBOX['maxX'] = int(wmsBBOX['centerX']+(160*scale/1000/2))
        wmsBBOX['minY'] = int(wmsBBOX['centerY']-(90*scale/1000/2))
        wmsBBOX['maxY'] = int(wmsBBOX['centerY']+(90*scale/1000/2))

        params = {
            'REQUEST': 'GetMap',
            'VERSION': self.appconfig.wms_version,
            'LAYERS': ",".join(layers),
            'SLD':  self.sld_url+self.pdfconfig.siteplanname+'_sld.xml',
            'SRS': self.appconfig.wms_srs,
            'BBOX': ",".join([str(wmsBBOX['minX']), str(wmsBBOX['minY']), str(wmsBBOX['maxX']), str(wmsBBOX['maxY'])]),
            'WIDTH': str(1600),
            'HEIGHT': str(900),
            'FORMAT': 'image/png',
            'TRANSPARENT': 'false'
        }

        getmapurl = self.crdppf_wms

        if getmapurl.find('?') < 0:
            getmapurl += '?'
        getmapurl = getmapurl + '&'.join(['%s=%s' % (key, value) for (key, value) in params.items()])

        http = httplib2.Http()

        h = dict(self.request.headers)
        if urlparse(getmapurl).hostname != 'localhost': 
            h.pop('Host')

        try:
            resp, content = http.request(getmapurl, method='GET', headers=h)
        except: 
            self.log.error("Unable to do GetMap request for url %s" % getmapurl)
            return None

        out = open(self.appconfig.tempdir+self.pdfconfig.siteplanname+'.png', 'wb')
        self.cleanupfiles.append(self.appconfig.tempdir+self.pdfconfig.siteplanname+'.png')
        out.write(content)
        out.close()

        self.sitemappath = self.appconfig.tempdir+self.pdfconfig.siteplanname+'.png'

    def add_topic(self, topic):
        """Adds a new entry to the topic list and sets it's category from:
            categorie = 0 : restriction not available - no layers
            categorie = 1 : restriction not touching the feature - layers, but no features (check geo availability)
            categorie = 2 : restriction touching the feature - layers and features
            categorie = 3 : restriction not legally binding - layers, features and complementary information
            defaults to 0 - restriction is not available
        """
        self.topiclist[str(topic.topicid)]={
            'categorie':0,
            'topicname':topic.topicname,
            'layers':{},
            'authority':topic.authority, 
            'topicorder':topic.topicorder,
            'authorityfk':topic.authorityfk,
            'publicationdate':topic.publicationdate
            }

        # if geographic layers are defined for the topic, get the list of all layers and then
        # check for each layer the information regarding the features touching the property
        if topic.layers:
            self.add_toc_entry(topic.topicid, '', str(topic.topicname.encode('iso-8859-1')), 1, '')
            for layer in topic.layers:
                self.topiclist[str(topic.topicid)]['layers'][layer.layerid]={
                    'layername':layer.layername,
                    'features':None
                    }
                # intersects a given layer with the feature and adds the results to the topiclist- see method add_layer
                self.add_layer(layer)
            self.get_topic_map(topic.layers, topic.topicid)
            # Get the list of documents related to a topic with layers and results
            if self.topiclist[str(layer.topicfk)]['categorie'] == 3:
                docfilters = [str(topic.topicid)]
                for doctype in self.doctypes:
                    docidlist = getDocumentReferences(docfilters)
                    self.topiclist[str(topic.topicid)][doctype] = self.set_documents(str(topic.topicid), doctype, docidlist, True)                
        else:
            if str(topic.topicid) in self.appconfig.emptytopics:
                self.topiclist[str(topic.topicid)]['layers'] = None
                self.topiclist[str(topic.topicid)]['categorie'] = 1
            else:
                self.topiclist[str(topic.topicid)]['layers'] = None
                self.topiclist[str(topic.topicid)]['categorie'] = 0

        # if legal povisions are defined for a topic the attributes are compiled in a list
        if 'legalprovision' in self.topiclist[topic.topicid].keys():
            self.get_legalprovisions(self.topiclist[str(topic.topicid)]['legalprovision'],topic.topicid)
        else:
            self.topiclist[str(topic.topicid)]['legalprovision']=None

        # if other references are defined for a topic the attributes are compiled in a list
        for doctype in self.doctypes:
            if doctype in self.topiclist[topic.topicid].keys():
                if doctype != 'legalbase' and  doctype != 'legalprovision':
                    self.get_references(self.topiclist[str(topic.topicid)][doctype],topic.topicid)
            else:
                if doctype != 'legalbase' and  doctype != 'legalprovision':
                    self.topiclist[str(topic.topicid)][doctype]=None

    def add_layer(self, layer):

        if self.log:
            self.log.warning("Running get feature")

        results = get_features_function(self.featureInfo['geom'],{'layerList':layer.layername,'id':self.featureid,'translations':self.translations})

        if self.log:
            self.log.warning("Done get feature")

        if results :
            self.layerlist[str(layer.layerid)]={'layername':layer.layername,'features':[]}
            for result in results:
                # for each restriction object we check for related documents
                docfilters = [str(result['id'])]
                for doctype in self.doctypes:
                    docidlist = getDocumentReferences(docfilters)
                    result['properties'][doctype] = self.set_documents(str(layer.topicfk), doctype, docidlist, False)
                self.layerlist[str(layer.layerid)]['features'].append(result['properties'])

            # we also check for documents on the layer level - if there are any results - else we don't need to bother
            docfilters = [layer.layername]
            for doctype in self.doctypes:
                docidlist = getDocumentReferences(docfilters)
                self.topiclist[str(layer.topicfk)]['layers'][layer.layerid][doctype] = self.set_documents(str(layer.topicfk), doctype, docidlist, True)

            self.topiclist[str(layer.topicfk)]['categorie']=3
            self.topiclist[str(layer.topicfk)]['no_page']='tocpg_'+str(layer.topicfk)
            self.topiclist[str(layer.topicfk)]['layers'][layer.layerid]['features']=self.layerlist[str(layer.layerid)]['features']
        else:
            self.layerlist[str(layer.layerid)]={'layername':layer.layername,'features':None}
            if self.topiclist[str(layer.topicfk)]['categorie'] != 3:
                self.topiclist[str(layer.topicfk)]['categorie']=1

    def set_documents(self, topicid, doctype, docids, geofilter):
        """ Function to fetch the documents related to the restriction:
        legal provisions, temporary provisions, references 
        """

        docs = {}
        documents = []
        
        if geofilter is True:
            filters = {
                'docids':docids,
                'topicid':topicid,
                'cadastrenb':self.featureInfo['numcom'],
                'chmunicipalitynb':self.featureInfo['nufeco']
            }
        else:
            filters = {'docids':docids}

        if len(docids) > 0:
            docs = getLegalDocuments(self.request,filters)
        else:
            docs['docs'] = []

        references = []
        # store the documents in a list
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
        
    def get_legalbases(self, legalbases, topicid):
        """Decomposes the object containing all legalbases related to a topic in a list
        """
        self.legalbaselist[str(topicid)]=[]
        for legalbase in legalbases:
            self.legalbaselist[str(topicid)].append({
                'officialtitle':legalbase.officialtitle,
                'title':legalbase.title,
                'abreviation':legalbase.abreviation,
                'officialnb':legalbase.officialnb,
                'legalbaseurl':legalbase.legalbaseurl,
                'canton':legalbase.canton,
                'commune':legalbase.commune,
                'legalstate':legalbase.legalstate,
                'publishedsince':legalbase.publishedsince,
                #'metadata':legalbase.metadata
                })
        self.topiclist[str(topicid)]['legalbases'] = self.legalbaselist[str(topicid)]

    def get_legalprovisions(self, legalprovisions, topicid):
        """Decomposes the object containing all legal provisions related to a topic in a list
        """
        self.legalprovisionslist[str(topicid)]=[]
        for provision in legalprovisions:
            self.legalprovisionslist[str(topicid)].append({
                'officialtitle': provision[u'officialtitle'],
                'title': provision['title'],
                'abreviation': provision['abbreviation'],
                'officialnb': provision['officialnb'],
                'legalprovisionurl':provision['remoteurl'],
                'canton': provision['state'],
                'commune': provision['municipalityname'],
                'legalstate': provision['legalstate'],
                'publishedsince': provision['publicationdate'],
                'sanctiondate': provision['sanctiondate'],
                'no_page': 'A'+str(len(self.appendix_entries))
                #'metadata':provision.metadata
                })
        self.topiclist[str(topicid)]['legalprovision'] = self.legalprovisionslist[str(topicid)]

    def get_references(self, references, topicid):
        """Decomposes the object containing all references related to a topic in a list
        """
        self.referenceslist[str(topicid)]=[]
        for reference in references:
            self.referenceslist[str(topicid)].append({
                'officialtitle': reference['officialtitle'],
                'title': reference['title'],
                'abreviation': reference['abbreviation'],
                'officialnb': reference['officialnb'],
                'legalprovisionurl': reference['remoteurl'],
                'canton': reference['state'],
                'commune': reference['municipalityname'],
                'legalstate': reference['legalstate'],
                'publishedsince': reference['publicationdate'],
                'sanctiondate': reference['sanctiondate'],
                'no_page': 'A'+str(len(self.appendix_entries))
                #'metadata':legalprovision.metadata
                })
        self.topiclist[str(topicid)]['references'] = self.referenceslist[str(topicid)]

    def get_wms_bbox(self):
        """ Defines the bounding box of the wms request
        """

        # Map scale
        scale = self.printformat['scale']

        # to recenter the map on the bbox of the feature, compute the best scale and add at least 10% of space we calculate a wmsBBOX
        wmsBBOX = {}
        wmsBBOX['centerY'] = int(self.mapconfig['bboxCenterY'])
        wmsBBOX['centerX'] = int(self.mapconfig['bboxCenterX'])
        # From the center point add and substract half the map distance in X and Y direction to get BBOX min/max coords
        wmsBBOX['minX'] = int(wmsBBOX['centerX']-(self.printformat['width']*scale/1000/2))
        wmsBBOX['maxX'] = int(wmsBBOX['centerX']+(self.printformat['width']*scale/1000/2))
        wmsBBOX['minY'] = int(wmsBBOX['centerY']-(self.printformat['height']*scale/1000/2))
        wmsBBOX['maxY'] = int(wmsBBOX['centerY']+(self.printformat['height']*scale/1000/2))
        wmsbbox = [
            (wmsBBOX['minX'], wmsBBOX['minY']), 
            (wmsBBOX['maxX'], wmsBBOX['minY']), 
            (wmsBBOX['maxX'], wmsBBOX['maxY']),
            (wmsBBOX['minX'], wmsBBOX['maxY'])
            ]
        return wmsBBOX, wmsbbox

    def get_topic_map(self,restriction_layers, topicid):
        """Produces the map and the legend for each layer of an restriction theme
        """
        # API GEO ADMIN EXAMPLE:
        # https://api.geo.admin.ch/feature/search?lang=en&layers=ch.bazl.projektierungszonen-flughafenanlagen&bbox=680585,255022,686695,259952&cb=Ext.ux.JSONP.callback

        wmsBBOX, wmsbbox = self.get_wms_bbox()

        if self.log:
            self.log.warning("DONE get_wms_bbox")

        # temp var to hold the parameters of the legend
        legend_layers = []
        # temp var for the path to the created legend
        legend_path = []
        complet_legend_path = []
        layers = []
        baselayers = []

        # Configure the WMS request to call either the internal or the external, federal WMS
        self.set_wms_config(topicid)
        if self.log:
            self.log.warning("DONE set_wms_config")

        # Adding each layer of the restriction to the WMS
        for restriction_layer in restriction_layers:
            # set the request parameters for either a call to the federal wms or to localhost
            if restriction_layer.topicfk in self.appconfig.ch_legend_layers.keys():
                legend_layers.append(self.appconfig.ch_legend_layers[str(restriction_layer.topicfk)])
                layers.append(self.appconfig.ch_legend_layers[str(restriction_layer.topicfk)])
                self.wms_get_legend['LAYER'] = self.appconfig.ch_legend_layers[str(restriction_layer.topicfk)]
                self.wms_get_styles['LAYERS'] = self.appconfig.ch_legend_layers[str(restriction_layer.topicfk)]
                # open an empty file for the layers legend graphic
                legend = open(self.appconfig.tempdir+self.filename+str('_legend_')+str(topicid)+'.png', 'wb')
                self.cleanupfiles.append(self.appconfig.tempdir+self.filename+str('_legend_')+str(topicid)+'.png')
                # define the legend path
                legend_path.append(self.appconfig.tempdir+self.filename+str('_legend_')+str(topicid))
            else:
                legend_layers.append(restriction_layer.layername)
                layers.append(restriction_layer.layername)
                self.wms_get_legend ['LAYER'] = restriction_layer.layername
                self.wms_get_styles['LAYERS'] = restriction_layer.layername
                legend = open(self.appconfig.tempdir+self.filename+str('_legend_')+str(restriction_layer.layername)+'.png', 'wb')
                self.cleanupfiles.append(self.appconfig.tempdir+self.filename+str('_legend_')+str(restriction_layer.layername)+'.png')
                legend_path.append(self.appconfig.tempdir+self.filename+str('_legend_')+str(restriction_layer.layername))

            # gets a list of all the categories of objects found in the map perimeter to reduce the legend
            legend_classes = set(self.get_legend_classes(wmsbbox,restriction_layer.layername))
            self.wms_get_legend['FORMAT'] = 'image/png'
            self.wms_get_legend['TRANSPARENT'] = self.wms_transparency

            getstylesurl = self.wms_url

            if getstylesurl.find('?') < 0:
                getstylesurl += '?'
            getstylesurl = getstylesurl + '&'.join(['%s=%s' % (key, value) for (key, value) in self.wms_get_styles.items()])

            http = httplib2.Http()

            h = dict(self.request.headers)
            if urlparse(getstylesurl).hostname != 'localhost': 
                h.pop('Host')

            if self.log:
                self.log.warning("WMS REQUEST")
                self.log.warning("on URL: %s", getstylesurl)
                self.log.warning('Doing layer: %s', restriction_layer.topicfk)

            try:
                resp, content = http.request(getstylesurl, method='GET', headers=h)
            except:
                if self.log:
                    self.log.error("Unable to do GetStyles request for url %s" % getstylesurl)
                return None

            if self.log:
                self.log.warning("DONE WMS REQUEST")

            dom = parseString(content)
            rules = dom.getElementsByTagName("Rule")

            complet_list = []
            # Remove all the classes from the xml which do not appear in the map extract
            for rule in rules:
                if len(rule.getElementsByTagName("ogc:Literal")) > 0:
                    literal = rule.getElementsByTagName("ogc:Literal")[0]
                    literal_value = literal.firstChild.nodeValue
                    complet_list.append(literal_value)
                    if literal_value not in legend_classes:
                        dynamic_legend = rule.parentNode
                        dynamic_legend.removeChild(rule)

            # write an sld file to filter the getLegendGraphic request with
            sld_legendfile = open(self.appconfig.tempdir+self.filename+str('_')+str(restriction_layer.layername)+'_legend_sld.xml', 'w')
            self.cleanupfiles.append(self.appconfig.tempdir+self.filename+str('_')+str(restriction_layer.layername)+'_legend_sld.xml')
            sld_legendfile.write(dom.toxml("utf-8"))
            sld_legendfile.close()

            # only necessary if complet legend should be called dynamically
            #complet_legend_body = urllib.urlencode(self.wms_get_legend)

            if self.log:
                self.log.warning("Applying SLD")

            if 'SLD' in self.wms_get_legend:
                del self.wms_get_legend['SLD']

            if self.log:
                self.log.warning("DONE Applying SLD")

            if sld_legendfile and topicid in [u'R073','R073','73',u'73']:
                legend_sld = self.sld_url+self.filename+str('_')+str(restriction_layer.layername)+'_legend_sld.xml'
                self.wms_get_legend['SLD'] = str(legend_sld)

            getsldurl = self.wms_url

            if getsldurl.find('?') < 0:
                getsldurl += '?'
            getsldurl = getsldurl + '&'.join(['%s=%s' % (key, value) for (key, value) in self.wms_get_legend.items()])

            http = httplib2.Http()

            h = dict(self.request.headers)
            if urlparse(getsldurl).hostname != 'localhost':
                h.pop('Host')

            try:
                resp, content = http.request(getsldurl, method='GET', headers=h)
            except:
                if self.log:
                    self.log.error("Unable to do GetMap request for url %s" % getsldurl)
                return None

            if topicid in self.appconfig.ch_topics:
                front = Image.open(StringIO(content))
                front = front.point(lambda x: x*0.7)
                legend = Image.new('RGBA', front.size, (255, 255, 255))
                legend.paste(front, (0, 0), front)
                legend = legend.convert('RGB')
                legend.save(self.appconfig.tempdir+self.filename+str('_legend_')+str(topicid)+'.png')
            else :
                legend.write(content)
                legend.close()

            if self.log:
                self.log.warning("DONE SLD on WMS")

        self.topiclist[topicid]['topiclegend'] = self.topiclegenddir+str(topicid)+'_topiclegend.pdf'

        if self.log:
            self.log.warning("WMS")

        params = (
            ('REQUEST', 'GetMap'),
            ('VERSION', self.appconfig.wms_version),
            ('LAYERS', ",".join(layers)),
            ('SRS', self.appconfig.wms_srs),
            ('BBOX', ",".join([str(wmsBBOX['minX']), str(wmsBBOX['minY']), str(wmsBBOX['maxX']), str(wmsBBOX['maxY'])])),
            ('WIDTH', str(self.mapconfig['width'])),
            ('HEIGHT', str(self.mapconfig['height'])),
            ('FORMAT', 'image/png'),
            ('TRANSPARENT', 'true')
        )

        getmapurl = self.wms_url
            
        if getmapurl.find('?') < 0:
            getmapurl += '?'
        getmapurl = getmapurl + '&'.join(['='.join(p) for p in params])

        if self.log:
            self.log.warning("On URL: %s", getmapurl)

        http = httplib2.Http()

        h = dict(self.request.headers)
        if urlparse(getmapurl).hostname != 'localhost':
            h.pop('Host')

        try:
            resp, content = http.request(getmapurl, method='GET', headers=h)
        except:
            if self.log:
                self.log.error("Unable to do GetMap request for url %s" % getmapurl)
            return None

        if self.log:
            self.log.warning("DONE WMS REQUEST")

        if self.log:
            self.log.warning("Writing image file")

        front_img = Image.open(StringIO(content))
        if restriction_layer.topicfk in self.appconfig.ch_topics:
            # reduce the opacity of the overlay image to 80% - it's a workaround for a transparency issue with FPDF and PNG 32bit
            front_img = front_img.point(lambda x: x*0.8)
        back_img = self.basemap
        back_img = back_img.convert('RGBA')
        back_img.paste(front_img, (0, 0), front_img)
        back_img = back_img.convert('RGB')
        back_img.save(self.appconfig.tempdir+self.filename+'_'+str(topicid)+'.png')
        self.cleanupfiles.append(self.appconfig.tempdir+self.filename+'_'+str(topicid)+'.png')

        if self.log:
            self.log.warning("Done - Writing image file")

        mappath = self.appconfig.tempdir+self.filename+'_'+str(topicid)+'.png'
        # Add the path to the thematic map and it's legendfile to the topiclist
        self.topiclist[topicid].update({'mappath':mappath,'legendpath':legend_path})

    def add_toc_entry(self, topicid, num, label, categorie, appendices):
        self.toc_entries[str(topicid)]={'no_page':num, 'title':label, 'categorie':int(categorie), 'appendices':set()}

    def get_toc(self):
        """Adding a table of content (TOC) to the document.
           categorie = 0 : restriction not available - no layers
           categorie = 1 : restriction not touching the feature - layers, but no features (check geo availability)
           categorie = 2 : restriction touching the feature - layers and features
           categorie = 3 : restriction not legally binding - layers and features and complementary inform
        """
        translations = self.translations
        pdfconfig = self.pdfconfig
        feature_info = self.featureInfo

        # START TOC
        self.add_page()
        self.set_margins(*pdfconfig.pdfmargins)
        self.set_y(40)
        self.set_font(*pdfconfig.textstyles['title3'])
        self.multi_cell(0, 12, translations['toclabel'])

        self.set_y(60)
        self.set_font(*pdfconfig.textstyles['bold'])
        self.cell(12, 15, '', '', 0, 'L')
        self.cell(118, 15, '', 'L', 0, 'L')
        self.cell(15, 15, '', 'L', 0, 'C')
        self.cell(15, 15, '', 'L', 1, 'C')

        self.cell(12, 5, translations['pagelabel'], 'B', 0, 'L')
        self.cell(118 , 5, translations['toclabel'], 'LB', 0, 'L')
        y = self.get_y()
        x = self.get_x()
        # Unfortunately there seems to be a bug in the pyfpdf library regarding the set_y function
        # when rotating - so we have to use a workaround rotating back and forth...
        self.set_xy(x+3.5, y+4)
        self.rotate(90)
        self.multi_cell(30, 4, translations['tocprovisionslabel'], 0,'L')
        self.rotate(0)
        self.set_xy(x+18, y+4)
        self.rotate(90)
        self.multi_cell(38, 4, translations['tocreferenceslabel'], 0,'L')
        self.rotate(0)
        self.set_xy(x, y)
        self.cell(15, 5, '', 'LB', 0, 'L')
        self.cell(15, 5, '', 'LB', 1, 'L')

        # List of all topics with a restriction for the selected parcel 
        for topic in self.topicorder.values():
            if self.topiclist[topic]['categorie'] == 3 :
                self.set_font(*pdfconfig.textstyles['bold'])
                if self.topiclist[topic]['no_page'] is not None:
                    self.cell(12, 6, self.topiclist[topic]['no_page'],'B', 0, 'L')
                else:
                    self.cell(12, 6, '', 'B', 0, 'C')
                self.cell(118, 6, self.topiclist[topic]['topicname'], 'LB', 0, 'L')
                if self.topiclist[topic]['legalprovision'] is not None :
                    pageslist = []
                    # Desactivated for now because it explodes the layout as it is for now!!
                    #~ for legalprovision in self.topiclist[topic]['legalprovision']:
                        #~ pageslist.append(legalprovision['no_page'])
                    self.cell(15, 6, ', '.join(pageslist), 'LB', 0, 'C')
                else:
                    self.cell(15, 6, '', 'LB', 0, 'L')
                self.cell(15, 6, '', 'LB', 1, 'L')

        self.ln()
        self.ln()
        self.set_font(*pdfconfig.textstyles['tocbold'])
        self.multi_cell(0, 6, translations['notconcerndbyrestrictionlabel'], 'B', 1, 'L')
        self.ln()

        for topic in self.topicorder.values():
            if self.topiclist[topic]['categorie'] == 1 :
                self.set_font(*pdfconfig.textstyles['tocbold'])
                self.cell(118, 6, self.topiclist[topic]['topicname'], '', 0, 'L')
                self.cell(15, 6, '', '', 0, 'L')
                self.cell(15, 6, '', '', 1, 'L')

        self.ln()
        self.set_font(*pdfconfig.textstyles['tocbold'])
        self.multi_cell(0, 6, translations['restrictionnotavailablelabel'], 'B', 1, 'L')
        self.ln()
        
        for topic in self.topicorder.values():
            if self.topiclist[topic]['categorie'] == 0 :
                self.set_font(*pdfconfig.textstyles['tocbold'])
                self.cell(118, 6,self.topiclist[topic]['topicname'],0,0,'L')
                self.cell(15, 6,'',0,0,'L')
                self.cell(15, 6,'',0,1,'L')

        if pdfconfig.optionaltopics == True :
            self.ln()
            self.set_font(*pdfconfig.textstyles['tocbold'])
            self.multi_cell(0, 5, translations['restrictionnotlegallybindinglabel'], 'B', 1, 'L')
            self.ln()

            self.set_font(*pdfconfig.textstyles['tocbold'])
            self.cell(118, 6, translations['norestrictionlabel'], 0, 0, 'L')
            self.cell(15, 6, str(''), 0, 0, 'L')
            self.cell(15, 6, str(''), 0, 1, 'L')

    def write_thematic_page(self, topic):
        """Writes the page for the given topic
        """
        # shorten the vars for convenience - check if still used
        translations = self.translations
        pdfconfig = self.pdfconfig
        feature_info = self.featureInfo

        # if the topic contains restrictions touching the feature add a page
        if self.topiclist[topic]['categorie'] > 2:
            self.add_page()
            self.set_margins(*pdfconfig.pdfmargins)
            tocpgalias = 'tocpg_'+str(topic)
            self.pages[2] = self.pages[2].replace(tocpgalias,str(self.page_no()))

            # Place the map
            self.image(self.topiclist[topic]['mappath'], 65, pdfconfig.headermargin, self.printformat['width'], self.printformat['height'])
            self.rect(65, pdfconfig.headermargin, self.printformat['width'], self.printformat['height'], '')
            # Define the size of the legend container
            legendbox_width = 40
            legendbox_height = self.printformat['height'] 
            legendbox_proportion = float(legendbox_width-4) / float(legendbox_height-20)

            # draw the legend container
            self.rect(pdfconfig.leftmargin, pdfconfig.headermargin, legendbox_width, legendbox_height, '')

            # define cells with border for the legend and the map
            self.set_xy(26, pdfconfig.headermargin+3)
            self.set_font(*pdfconfig.textstyles['bold'])
            self.cell(50, 6, translations['bboxlegendlabel'], 0, 1, 'L')
            y= self.get_y()
            self.set_font(*pdfconfig.textstyles['normal'])
            if  len(self.topiclist[topic]['legendpath']) > 0:
                max_legend_width_px = 0
                tot_legend_height_px = 0
                sublegends = []

                for graphic in self.topiclist[topic]['legendpath']:
                    tempimage = Image.open(str(graphic)+'.png')
                    legend_width_px, legend_height_px = tempimage.size
                    sublegends.append([graphic,legend_width_px, legend_height_px])
                    if legend_width_px > max_legend_width_px :
                        max_legend_width_px = legend_width_px
                    tot_legend_height_px += legend_height_px

                # number of px per mm of legend width = width proportion
                width_proportion = float(max_legend_width_px) / float(legendbox_width-4)
                height_proportion = float(tot_legend_height_px) / float(legendbox_height-20)
                
                # check if using this proportion of px/mm the totol_legend_height fits 
                # in the available space else fit the height and adapt width
                supposed_height_mm = float(tot_legend_height_px) / width_proportion
                if supposed_height_mm < float(legendbox_height-20) : 
                    limit_proportion = width_proportion
                else : 
                    limit_proportion = height_proportion
                    
                if limit_proportion < 5:
                    limit_proportion = 5

                for path, width, height in sublegends:
                    y = self.get_y()
                    legend = self.image(path+'.png',26, y, float(width)/limit_proportion)
                    self.set_y(y+(float(height)/limit_proportion))

            self.set_y(40)
            self.set_font(*pdfconfig.textstyles['title3'])
            self.multi_cell(0, 6, str(self.topiclist[topic]['topicname'].encode('iso-8859-1')), 0, 1, 'L')
            y = self.get_y()
            self.set_y(y+110)

            #Display the URL to the complete legend
            self.set_font(*pdfconfig.textstyles['bold'])
            self.cell(55, 5, translations['completlegendlabel'], 0, 0, 'L')
            self.set_font(*pdfconfig.textstyles['normal'])
            if 'topiclegend' in self.topiclist[topic] and self.topiclist[topic]['topiclegend'] is not None:
                self.set_text_color(*self.pdfconfig.urlcolor)
                self.cell(120, 5, self.topiclist[topic]['topiclegend'], 0, 1, 'L')
                self.set_text_color(*self.pdfconfig.defaultcolor)
            else:
                self.cell(120, 5, translations['nocompletelegendtext'], 0, 1, 'L')
            
            #Get the restrictions
            y = self.get_y()
            self.set_y(y+5)
            if self.topiclist[topic]['layers']:
                i = 0
                # for each layer we check if there are features
                for layer in self.topiclist[topic]['layers']:
                    if self.topiclist[topic]['layers'][layer]['features']:
                        i += 1
                        self.set_font(*pdfconfig.textstyles['bold'])
                        if i == 1:
                            self.cell(55, 5, translations['contentlabel'].encode('iso-8859-1'), 0, 0, 'L')
                        else:
                            self.cell(55, 5, '', 0, 0, 'L')
                        self.set_font(*pdfconfig.textstyles['normal'])
                        content = ''
                        for feature in self.topiclist[topic]['layers'][layer]['features']:
                            if 'teneur' in feature.keys():
                                if feature['statutjuridique'] is None:
                                    feature['statutjuridique'] = 'None'
                                if feature['teneur'] is None:
                                    feature['teneur'] = 'None'
                                if feature['geomType'] == 'area':
                                    content += feature['teneur'].encode('iso-8859-1') \
                                        +str(' \t(')+feature['intersectionMeasure'].replace(' : ', translations['areaMeasureLabel']).encode('iso-8859-1')+str(')\n')
                                elif feature['geomType'] == 'line': 
                                    content += feature['teneur'].encode('iso-8859-1') \
                                        +str(' \t(')+feature['intersectionMeasure'].replace(' : ', translations['distanceMeasureLabel']).encode('iso-8859-1')+str(')\n')
                                else: 
                                    content += feature['teneur'].encode('iso-8859-1')+str('\n')
                                for doctype in self.doctypes:
                                    if len(feature[doctype]) > 0:
                                        for document in feature[doctype]:
                                            content += document['officialtitle'].encode('iso-8859-1')+'\n'
                            else:
                                for property,value in feature.iteritems():
                                    if value is not None and property != 'featureClass':
                                        if isinstance(value, float) or isinstance(value, int):
                                            value = str(value)
                                        content += value.encode('iso-8859-1')
                        for doctype in self.doctypes:
                            if len(self.topiclist[topic]['layers'][layer][doctype]) > 0:
                                for document in self.topiclist[topic]['layers'][layer][doctype]:
                                    content += document['officialtitle'].encode('iso-8859-1')+'\n'
                        self.multi_cell(100, 5, content, 0, 1, 'L')
            else:
                self.multi_cell(100, 5, 'Error in line 818', 0, 1, 'L')
                
            # For all document types we get the references and list them:
            # legalprovisions = Legal Provisions/Dispositions juridiques/Gesetzliche Bestimmungen
            # references = References and complementary information/Informations et renvois supplémentaires/Verweise und Zusatzinformationen
            # temporaryprovisions = Ongoing amendments/Modifications en cours/Laufende Änderungen
            # map = Maps and plans/Cartes et plans/Karten und Pläne
            for doctype in self.doctypes:
                # for now we ignore different document types
                if doctype not in ['legalbase']:
                    y = self.get_y()
                    self.set_y(y+5)
                    self.set_font(*pdfconfig.textstyles['bold'])
                    doctypelabel = doctype+'slabel'
                    self.cell(55, 5, translations[doctypelabel], 0, 0, 'L')
                    self.set_font(*pdfconfig.textstyles['normal'])
                    if doctype in self.topiclist[topic].keys() and len(self.topiclist[topic][doctype]) > 0:
                        for document in self.topiclist[topic][doctype]:
                            self.set_x(80)
                            self.multi_cell(0, 5, unicode(document['officialtitle']).encode('iso-8859-1'))
                    else:
                        self.set_x(80)
                        self.multi_cell(0, 5, translations['nodocumenttext'])

            # Competent Authority/Service competent/Zuständige Behörde
            y = self.get_y()
            self.set_y(y+5)
            self.set_font(*pdfconfig.textstyles['bold'])
            self.cell(55, 5, translations['competentauthoritylabel'], 0, 0, 'L')
            self.set_font(*pdfconfig.textstyles['normal'])
            
            if self.topiclist[topic]['authority'].authorityname is not None:
                self.cell(120, 5, self.topiclist[topic]['authority'].authorityname.encode('iso-8859-1'), 0, 1, 'L')
            else :
                self.cell(120, 5, translations['noauthoritytext'], 0, 1, 'L')
            if self.topiclist[topic]['authority'].authoritydepartment is not None:
                self.cell(55, 5, str(' '), 0, 0, 'L')
                self.cell(120, 5, self.topiclist[topic]['authority'].authoritydepartment.encode('iso-8859-1'), 0, 1, 'L')
            if self.topiclist[topic]['authority'].authorityphone1 is not None:
                self.cell(55, 5, str(' '), 0, 0, 'L')
                self.cell(120, 5, translations['phonelabel']+self.topiclist[topic]['authority'].authorityphone1.encode('iso-8859-1'), 0, 1, 'L')
            if self.topiclist[topic]['authority'].authoritywww is not None:
                self.cell(55, 5, str(' '), 0, 0, 'L')
                self.set_text_color(*self.pdfconfig.urlcolor)
                self.cell(120, 5, self.topiclist[topic]['authority'].authoritywww.encode('iso-8859-1'),0,1,'L')
                self.set_text_color(*self.pdfconfig.defaultcolor)

            # Legal bases/Bases légales/Gesetzliche Grundlagen
            y = self.get_y()
            self.set_y(y+5)
            self.set_font(*pdfconfig.textstyles['bold'])
            self.cell(55, 5, translations['legalbaseslabel'], 0, 0, 'L')
            self.set_font(*pdfconfig.textstyles['normal'])
            if self.topiclist[topic]['legalbase']:
                for legalbase in self.topiclist[topic]['legalbase']:
                    self.set_x(80)
                    self.multi_cell(0, 5, legalbase['officialnb']+' : '+legalbase['officialtitle'], 0, 1, 'L')
                    self.set_x(80)
                    self.set_font(*self.pdfconfig.textstyles['url'])
                    self.set_text_color(*self.pdfconfig.urlcolor)
                    self.multi_cell(0, 4, 'URL : '+legalbase['remoteurl'])
                    self.set_text_color(*self.pdfconfig.defaultcolor)
                    self.set_font(*self.pdfconfig.textstyles['normal'])
            else:
                self.multi_cell(0, 5, translations['nodocumenttext'])

    def add_appendix(self, topicid, num, label, url, filepath):
        self.appendix_entries.append({'topicid':topicid, 'no_page':num, 'title':label, 'url':url, 'path':filepath})
        if self.toc_entries[str(topicid)] :
            self.toc_entries[topicid]['appendices'].add(num)
        else:
            pass

    def add_reference(self, topicid, num, label,url):
        self.reference_entries.append({'topicid':topicid, 'no_page':num, 'title':label, 'url':url})
        if self.toc_entries[str(topicid)] :
            self.toc_entries[topicid]['reference'].add(num)
        else:
            pass

    def get_appendices(self):
        """Adding a list of appendix to the document."""
        translations = self.translations
        pdfconfig = self.pdfconfig
        feature_info = self.featureInfo

        # START APPENDIX
        self.add_page()
        self.set_margins(*pdfconfig.pdfmargins)
        self.set_y(40)
        self.set_font(*pdfconfig.textstyles['title3'])
        self.multi_cell(0, 12, translations['appendiceslistlabel'])

        self.set_y(60)
        self.set_font(*pdfconfig.textstyles['bold'])
        self.cell(15, 6, translations['pagelabel'], 0, 0, 'L')
        self.cell(135, 6, translations['appendicestitlelabel'], 0, 1, 'L')


    def Appendices(self):
        """ Creates a new page with a list of appendices and depending on the
            extract type the url to the document
        """

        self.add_page()
        self.set_margins(*self.pdfconfig.pdfmargins)
        self.set_y(40)
        self.set_font(*self.pdfconfig.textstyles['title3'])
        self.multi_cell(0, 12, self.translations['appendiceslistlabel'])

        self.set_y(60)
        self.set_font(*self.pdfconfig.textstyles['bold'])
        self.cell(15, 6, self.translations['pagelabel'], 0, 0, 'L')
        self.cell(135, 6, self.translations['appendicestitlelabel'], 0, 1, 'L')
        
        index = 1
        if len(self.appendix_entries) > 0:
            for appendix in self.appendix_entries:
                self.set_font(*self.pdfconfig.textstyles['tocbold'])
                self.appendix_links.append(self.add_link())
                self.cell(15, 6, str('A'+str(index)), 0, 0, 'L')
                self.multi_cell(0, 6, appendix['title'], 0, 'L')
                if self.reportInfo['type'] == 'reduced' or self.reportInfo['type'] == 'reducedcertified':
                    self.set_x(40)
                    self.set_font(*self.pdfconfig.textstyles['tocurl'])
                    self.set_text_color(*self.pdfconfig.urlcolor)
                    self.multi_cell(0, 5, str(appendix['url']))
                    self.set_text_color(*self.pdfconfig.defaultcolor)
                index += 1
        else:
            self.multi_cell(0, 5, self.translations['nodocumenttext'])

    def clean_up_temp_files(self):
        """ Removes the temporary files needed to create an extract:
            sld files, legend files, map files
        """

        for tempfile in self.cleanupfiles:
            remove(str(tempfile))
