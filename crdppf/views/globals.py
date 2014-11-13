# -*- coding: UTF-8 -*-
from pyramid.view import view_config
from crdppf.models import DBSession, Translations

@view_config(route_name='initjs', renderer='crdppf:templates/derived/init.js')
def initjs(request):
    session = request.session
    
    # Define language to get multilingual labels for the selected language
    # defaults to 'fr': french - this may be changed in the appconfig
    if 'lang' not in session:
        lang = request.registry.settings['default_language'].lower()
    else : 
        lang = session['lang'].lower()
        
    # GO into DB
    # Get translations
    # Add to d
    locals = {}
    lang_dict = {
        'fr': Translations.fr,
        'de': Translations.de,
        'it': Translations.it,
        'en': Translations.en
    }
    translations = DBSession.query(Translations.varstr, lang_dict[lang]).all()
    for key, value in translations :
        locals[str(key)] = value
        
    sdf
    d = {
        'crdppf_fr_car': 'voiture',
    }
    
    request.response.content = 'application/javascript'
    
    return locals
    
    
@view_config(route_name='globalsjs', renderer='crdppf:templates/derived/globals.js')
def globalsjs(request):
    request.response.content = 'application/javascript'
    d = {}
    return d