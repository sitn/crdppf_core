# -*- coding: UTF-8 -*-
from pyramid.view import view_config

from crdppf.models import DBSession
from crdppf.models.models import Translations, Layers


@view_config(route_name='initjs', renderer='crdppf:templates/derived/init.js')
def initjs(request):
    session = request.session

    # Define language to get multilingual labels for the selected language
    # defaults to 'fr': french - this may be changed in the appconfig
    if 'lang' not in session:
        lang = request.registry.settings['default_language'].lower()
    else:
        lang = session['lang'].lower()

    lang_dict = {
        'fr': Translations.fr,
        'de': Translations.de,
        'it': Translations.it,
        'en': Translations.en
    }

    locals = {}

    translations = DBSession.query(Translations.varstr, lang_dict[lang]).all()
    for key, value in translations:
        if value is not None:
            locals[str(key)] = value.replace("'", "\\'").replace("\n", "\\n")
        else:
            locals[str(key)] = ''

    layerlist = []
    baselayers = []
    # get all layers
    layers = DBSession.query(Layers).order_by(Layers.layerid).all()
    baselayerexists = False
    for layer in layers:
        if layer.baselayer is True:
            baselayerexists = True
            layerDico = {}
            layerDico['id'] = layer.layerid
            layerDico['image'] = layer.image
            layerDico['name'] = layer.layername
            layerDico['wmtsname'] = layer.wmtsname
            layerDico['tile_format'] = layer.tile_format
            baselayers.append(layerDico)
        else:
            layerlist.append({
                'layerid': layer.layerid,
                'layername': layer.layername.replace("'", "\\'"),
                'layerdescription': layer.layerdescription.replace("'", "\\'"),
                'layeravailability': layer.layeravailability.replace("'", "\\'"),
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
    if baselayerexists is False:
        if request.registry.settings['defaultTiles']:
            defaultTiles = {}
            defaultlayer = str(request.registry.settings['defaultTiles']).split(',')
            for param in defaultlayer:
                key, value = param.replace("'", '').split(':')
                defaultTiles[key] = value
            layerDico = {}
            layerDico['id'] = '9999'
            layerDico['image'] = None
            layerDico['name'] = 'default_layer'
            layerDico['wmtsname'] = defaultTiles['wmtsname']
            layerDico['tile_format'] = defaultTiles['tile_format']
            baselayers.append(layerDico)

    try:
        disclaimer = request.registry.settings['disclaimer']
        if disclaimer == 'False' or request.registry.settings['disclaimer'] == 'false':
            disclaimer = False
    except:
        disclaimer = True

    init = {'fr': locals, 'layerlist': layerlist, 'baseLayers': baselayers, 'disclaimer': disclaimer}
    request.response.content = 'application/javascript'

    return init


@view_config(route_name='globalsjs', renderer='crdppf:templates/derived/globals.js')
def globalsjs(request):
    request.response.content = 'application/javascript'
    d = {}
    return d
