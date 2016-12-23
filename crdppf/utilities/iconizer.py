# -*- coding: UTF-8 -*-
"""
FileName: iconizer.py
=============================================================================
Creates all the symbols to generate the dynamic legend for the PDF extract
=============================================================================
Created: [2016/12/19]
Author: François Voisard
"""

import os.path
import argparse
import yaml

from pyramid.paster import get_app

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

    get_app(app_config)
    from crdppf.models import DBSession, Layers
    
    session = DBSession()
    layers = session.query(Layers).all()
    for layer in layers:
        iconizer(layer)


def iconizer(restriction_layer):
    """ script to create a symbol 
    """

    print restriction_layer.layername
    
    return

def iconizer_copy(restriction_layers):
        # Adding each layer of the restriction to the WMS
    for restriction_layer in restriction_layers:
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

    return

if __name__ == "__main__":
    main()
    #iconizer()
