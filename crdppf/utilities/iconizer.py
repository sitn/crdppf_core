# -*- coding: UTF-8 -*-
"""
FileName: iconizer.py
=============================================================================
Creates all the symbols to generate the dynamic legend for the PDF extract
=============================================================================
Created: [2016/12/19]
Updated: [2017/03/22]
Author: François Voisard
"""

import os.path
import pkg_resources
import argparse

import httplib2
from urllib import urlencode

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

    if not os.path.isfile(app_config):
        parser.error("Cannot find config file: {0!s}".format(app_config))

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

    from crdppf.models import DBSession, Layers

    session = DBSession()
    layers = session.query(Layers).all()
    for layer in layers:
        if layer.baselayer is False:
            iconizer(layer, wmsconfigs, configs)


def set_wms_config(configs):
    """ Sets the basic WMS parameters in function of the topic
    """

    wmsurl = configs['crdppf_wms']
    wms_get_styles = {
        'REQUEST': 'GetStyles'
        }
    wms_get_legend = {
        'REQUEST': 'GetLegendGraphic',
        'TRANSPARENT': configs['wms_transparency']
    }
    wms_params = {
        'SERVICE': 'WMS',
        'VERSION': str(configs['wms_version']),
        'SRS': str(configs['wms_srs']),
        'lang': configs['lang']
        }
    for key, value in wms_params.iteritems():
        wms_get_legend[key] = value
        wms_get_styles[key] = value

    return {'baseurl': wmsurl, 'getlegend': wms_get_legend, 'getstyles': wms_get_styles}


def iconizer(restriction_layer, wmsconfigs, configs):
    """ script to create a symbol for each class of the PLR map layers
    """

    tempdir = pkg_resources.resource_filename('crdppfportal', 'static/public/temp_files/')
    iconsdir = pkg_resources.resource_filename('crdppfportal', 'static/images/icons/')
    sld_url = configs['localhost_url'] + str('/proj/public/temp_files/')

    # compile and call getStyles query
    getstylesurl = wmsconfigs['baseurl']
    wms_get_styles = wmsconfigs['getstyles']
    wms_get_styles['LAYERS'] = restriction_layer.layername

    if getstylesurl.find('?') < 0:
        getstylesurl += '?'
    getstylesurl = getstylesurl + urlencode(wms_get_styles.items())

    http = httplib2.Http()

    try:
        resp, content = http.request(getstylesurl, method='GET')
    except:
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

            if len(rule.getElementsByTagName("ogc:Literal")) > 0:
                literal = rule.getElementsByTagName("ogc:Literal")[0]
                class_name = rule.getElementsByTagName("Name")[0].firstChild.nodeValue
                literal_value = literal.firstChild.nodeValue
                if literal_value == '.':
                    literal_value = 'autre_'+str(restriction_layer.layername)
                literal_value = literal_value.replace(' ', '_').replace('.', '_')

                # write an sld file with all classes to create an icon for each class
                sld_legendfile = open(tempdir+literal_value.encode('utf-8')+'_legend_sld.xml', 'w')
                sld_legendfile.write(dom.toxml("utf-8"))
                sld_legendfile.close()

                # compile and call getLegendGraphic query
                wms_get_legend = wmsconfigs['getlegend']
                wms_get_legend['FORMAT'] = 'image/png'
                wms_get_legend['LAYER'] = restriction_layer.layername.encode('UTF-8')
                wms_get_legend['RULE'] = class_name.encode('UTF-8')

                if 'SLD' in wms_get_legend:
                    del wms_get_legend['SLD']

                legend_sld = sld_url+literal_value.encode('utf-8')+'_legend_sld.xml'
                wms_get_legend['SLD'] = str(legend_sld)

                getsldurl = wmsconfigs['baseurl']

                if getsldurl.find('?') < 0:
                    getsldurl += '?'
                getsldurl = getsldurl + urlencode(wms_get_legend.items())

                http = httplib2.Http()

                try:
                    resp, content1 = http.request(getsldurl, method='GET')
                except:
                    return None
                icon = open(iconsdir+literal_value.encode('utf-8')+'.png', 'wb')
                icon.write(content1)
                icon.close()
            else:
                return

    return

if __name__ == "__main__":
    main()
