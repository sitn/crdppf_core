# -*- coding: UTF-8 -*-
from pyramid.view import view_config

from crdppf.models import DBSession, Translations, Layers

@view_config(route_name='initjs', renderer='crdppf:templates/derived/init.js')
def initjs(request):
    session = request.session
    
    # Define language to get multilingual labels for the selected language
    # defaults to 'fr': french - this may be changed in the appconfig
    if 'lang' not in session:
        lang = request.registry.settings['default_language'].lower()
    else : 
        lang = session['lang'].lower()

    lang_dict = {
        'fr': Translations.fr,
        'de': Translations.de,
        'it': Translations.it,
        'en': Translations.en
    }
    
    locals = {}
    
    translations = DBSession.query(Translations.varstr, lang_dict[lang]).all()
    for key, value in translations :
        if value is not None:
            locals[str(key)] = value.replace("'","\\'").replace("\n","\\n")
        else:
            locals[str(key)] = ''

    layerlist = []
    baselayers = []
    # get all layers
    layers = DBSession.query(Layers).all()
    for layer in layers:
        if layer.baselayer == True:
            layerDico = {}
            layerDico['id'] = layer.layerid
            layerDico['image'] = layer.image
            layerDico['name'] = layer.layername
            layerDico['wmtsname'] = layer.wmtsname
            baselayers.append(layerDico)
        else:
            layerlist.append({
                'layerid': layer.layerid,
                'layername': layer.layername.replace("'","\\'"),
                'layerdescription': layer.layerdescription.replace("'","\\'"),
                'layeravailability': layer.layeravailability.replace("'","\\'"),
                'wmtsname': layer.wmtsname,
                'layermetadata': layer.layermetadata,
                'assentdate': layer.assentdate,
                'baselayer': layer.baselayer,
                'image': layer.image,
                'publicationdate': layer.publicationdate,
                'theme_id':  layer.theme_id,
                'updatedate': layer.updatedate,
                'topicfk': layer.topicfk
            })

    init = {'fr': locals,'layerlist': layerlist, 'baseLayers': baselayers}
    request.response.content = 'application/javascript'
    
    return init
    
@view_config(route_name='globalsjs', renderer='crdppf:templates/derived/globals.js')
def globalsjs(request):
    request.response.content = 'application/javascript'
    d = {}
    return d