# -*- coding: UTF-8 -*-
"""
FileName: iconizer.py
=============================================================================
Creates all the symbols to generate the dynamic legend for the PDF extract
=============================================================================
Created: [2016/12/19]
Updated: [2017/02/13]
Author: François Voisard
"""

import os.path
import pkg_resources
import argparse
import yaml

import httplib2
from urlparse import urlparse

from pyramid.paster import get_app
from xml.dom.minidom import parseString

def main():
    """ Script to parse all the icons for the legends of the public land restrictions application
    """

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i", "--app-config",
        default="production.ini", dest="app_config",
        help="The application .ini config file (optional, default is "
        "'production.ini')"
    )
    parser.add_argument(
        "-d", "--db-config",
        default="config_db.yaml", dest="db_config",
        help="The application db config file (optional, default is "
        "'config_db.yaml')"
    )
    parser.add_argument(
        "-p", "--pdf-config",
        default="config_pdf.yaml", dest="pdf_config",
        help="The application pdf config file (optional, default is "
        "'config_pdf.yaml')"
    )

    options = parser.parse_args()
    app_config = options.app_config
    db_config = options.db_config
    pdf_config = options.pdf_config
    
    if not os.path.isfile(app_config):
        parser.error("Cannot find config file: {0!s}".format(app_config))
    
    if not os.path.isfile("config_db.yaml"):
        parser.error("Cannot find the database config file: {0!s}".format(db_config))
        exit(1)
    with open("config_db.yaml", "r") as db_config:
        dbconfig = yaml.load(db_config)

    if not os.path.isfile("config_pdf.yaml"):
        parser.error("Cannot find the pdf config file: {0!s}".format(pdf_config))
        exit(1)
    with open("config_pdf.yaml", "r") as pdf_config:
        pdfconfig = yaml.load(pdf_config)
    
    # Ignores pyramid deprecation warnings
    #~ warnings.simplefilter("ignore", DeprecationWarning)

    myapp = get_app(app_config)
    configs = {}
    
    for key, value in myapp.registry.settings.iteritems():
        configs[key] = value
        if key == 'app_config':
            for k, v in configs['app_config'].iteritems():
                configs[k] = v
        if key == 'pdf_config':
            for k, v in configs['pdf_config'].iteritems():
                configs[k] = v
     
    wmsconfigs = set_wms_config(configs)
    
    from crdppf.models import DBSession, Topics, Layers
    
    session = DBSession()
    topics = session.query(Topics).all()
    layers = session.query(Layers).all()
    for layer in layers:
        if layer.baselayer == False and layer.layername not in ['r132_perimetre_prot_eau','r131_zone_prot_eau']:
            iconizer(layer, wmsconfigs, configs)


def set_wms_config(configs):
    """ Sets the basic WMS parameters in function of the topic
    """

    wmsurl = configs ['crdppf_wms'] 
    wms_get_styles = {
        'REQUEST': 'GetStyles'
        }
    wms_get_legend = {
        'REQUEST': 'GetLegendGraphic',
        'TRANSPARENT': configs['wms_transparency']
    }
    wms_params = {
        'SERVICE': 'WMS',
        'VERSION': str(configs['wms_version']) ,
        'SRS': str(configs['wms_srs']),
        'lang':configs['lang']
        }
    for key, value in wms_params.iteritems():
        wms_get_legend[key] = value
        wms_get_styles[key] = value
    
    return {'baseurl': wmsurl, 'getlegend': wms_get_legend, 'getstyles': wms_get_styles}


def iconizer(restriction_layer, wmsconfigs, configs):
    """ script to create a symbol for each class of the PLR map layers
    """
    
    layers = []
    
    tempdir = pkg_resources.resource_filename('crdppfportal', 'static/public/temp_files/')
    iconsdir = str(configs['imagesbasedir'])+str('/icons')
    sld_url = configs ['localhost_url'] +str('/proj/public/temp_files/')
    
    # compile and call getStyles query
    getstylesurl = wmsconfigs['baseurl']
    wms_get_styles =wmsconfigs['getstyles']
    wms_get_styles['LAYERS'] = restriction_layer.layername

    if getstylesurl.find('?') < 0:
        getstylesurl += '?'
    getstylesurl = getstylesurl + '&'.join(['%s=%s' % (key, value) for (key, value) in wms_get_styles.items()])

    http = httplib2.Http()

    #~ h = dict(request.headers)
    #~ if urlparse(getstylesurl).hostname != 'localhost': 
        #~ h.pop('Host')

    try:
        resp, content = http.request(getstylesurl, method='GET')
    except:
        if log:
            log.error("Unable to do GetStyles request for url %s" % getstylesurl)
        return None

    origin = parseString(content)
    rules = origin.getElementsByTagName("Rule")
    sld_legendfile = open(tempdir+str(restriction_layer.layername)+'_origin_legend_sld.xml', 'w')
    sld_legendfile.write(origin.toxml("utf-8"))
    sld_legendfile.close()

    if rules.length > 0:
        for rule in rules:
            dom = parseString(content)
            try: 
                fts = dom.getElementsByTagName("FeatureTypeStyle")[0]
                fts_up = fts.parentNode
                fts_up.removeChild(fts)
                fts_up.appendChild(dom.createElement("FeatureTypeStyle"))
                fts = dom.getElementsByTagName("FeatureTypeStyle")[0]
                fts.appendChild(rule)
            except:
                pass
            #~ print dom.toxml("utf-8")

            if len(rule.getElementsByTagName("ogc:Literal")) > 0:
                literal = rule.getElementsByTagName("ogc:Literal")[0]
                class_name = rule.getElementsByTagName("Name")[0].firstChild.nodeValue
                literal_value = literal.firstChild.nodeValue
                if literal_value == '.':
                    literal_value = 'autre_'+str(restriction_layer.layername)
                literal_value.replace(' ','_')
                #~ # write an sld file with all classes to create an icon for each class
                sld_legendfile = open(tempdir+str(literal_value)+'_legend_sld.xml', 'w')
                sld_legendfile.write(dom.toxml("utf-8"))
                sld_legendfile.close()
                
                # compile and call getLegendGraphic query
                wms_get_legend =wmsconfigs['getlegend']
                wms_get_legend['FORMAT'] = 'image/png'
                wms_get_legend['LAYER'] = restriction_layer.layername
                wms_get_legend['RULE'] = class_name

                if 'SLD' in wms_get_legend:
                    del wms_get_legend['SLD']

                legend_sld = sld_url+str(literal_value)+'_legend_sld.xml'
                wms_get_legend['SLD'] = str(legend_sld)

                getsldurl = wmsconfigs['baseurl']

                if getsldurl.find('?') < 0:
                    getsldurl += '?'
                getsldurl = getsldurl + '&'.join(['%s=%s' % (key, value) for (key, value) in wms_get_legend.items()])
                print getsldurl

                http = httplib2.Http()

                try:
                    resp, content = http.request(getsldurl, method='GET')
                except:
                    if log:
                        log.error("Unable to do GetLegend request for url %s" % getsldurl)
                    return None

            else:
                return


    return

if __name__ == "__main__":
    main()
    #iconizer()
