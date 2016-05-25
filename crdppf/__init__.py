# -*- coding: utf-8 -*-
from pyramid.config import Configurator
from sqlalchemy import engine_from_config
import sqlahelper
from pyramid.session import UnencryptedCookieSessionFactoryConfig

from pyramid_mako import add_mako_renderer

from papyrus.renderers import GeoJSON
import papyrus

import os
import yaml

# GET THE INITIAL CONFIGURATION FROM THE DB
def read_app_config(settings):
    """
    Read the initial app config
    """
    from crdppf.models import DBSession, Base, AppConfig

    results = {}
    results = DBSession.query(AppConfig).all()

    for result in results :
        settings['app_config'].update({str(result.parameter):str(result.paramvalue)})

    return True
   
# INCLUDE THE CORE CONFIGURATION AND CREATE THE APPLICATION   
def includeme(config):
    """ This function returns a Pyramid WSGI application.
    """
    
    settings = config.get_settings()
    
    engine = engine_from_config(
        settings,
        'sqlalchemy.',
        convert_unicode=False,
        encoding='utf-8'
        )
    sqlahelper.add_engine(engine)

    global db_config
    db_config = yaml.load(file(settings.get('db.cfg')))['db_config']
    settings.update(yaml.load(file(settings.get('app.cfg'))))

    config.include(papyrus.includeme)
    config.include('pyramid_mako')
    # bind the mako renderer to other file extensions
    add_mako_renderer(config, ".js")

    config.add_renderer('geojson', GeoJSON())

    # add app configuration from db
    read_app_config(settings)

    specific_tmp_path = os.path.join(settings['specific_root_dir'], 'templates')
    specific_static_path = os.path.join(settings['specific_root_dir'], 'static')
    settings.setdefault('mako.directories',['crdppf:templates', specific_tmp_path])
    settings.setdefault('reload_templates',True)
    
    # add the static view (for static resources)
    config.add_static_view('static', 'crdppf:static',cache_max_age=3600)
    config.add_static_view('proj', 'crdppfportal:static', cache_max_age=3600)
     
    # ROUTES
    config.add_route('home', '/')
    config.add_route('images', '/static/images/')
    config.add_route('create_extract', 'create_extract')
    config.add_route('get_features', 'get_features')
    config.add_route('get_property', 'property/get')
    config.add_route('set_language', 'set_language')
    config.add_route('get_language', 'get_language')
    config.add_route('get_translation_dictionary', 'get_translation_dictionary')
    config.add_route('get_translations_list', 'get_translations_list')
    config.add_route('get_interface_config', 'get_interface_config')
    config.add_route('get_baselayers_config', 'get_baselayers_config')
    config.add_route('test', 'test')
    config.add_route('formulaire_reglements', 'formulaire_reglements')
    config.add_route('getTownList', 'getTownList')
    config.add_route('getTopicsList', 'getTopicsList')
    config.add_route('createNewDocEntry', 'createNewDocEntry')
    config.add_route('document_ref', 'getDocumentReferences')
    config.add_route('legal_documents', 'getLegalDocuments')
    config.add_route('map', 'map')
    config.add_route('configpanel', 'configpanel')
    
    config.add_route('initjs', '/init.js')
    config.add_route('globalsjs', '/globals.js')

    config.add_route('ogcproxy', '/ogcproxy')
    
    # CLIENT VIEWS
    config.add_view('crdppf.views.entry.Entry', route_name = 'images')
    config.add_view('crdppf.views.entry.Entry', route_name='test')

    # Print proxy routes
    config.add_route('printproxy_report_get', '/printproxy/report/{ref}')
    config.add_route('printproxy_status', '/printproxy/status/{ref}.json')
    config.add_route('printproxy_report_create', '/printproxy/report/{type_}/{idemai}')

    # ADMIN VIEWS
    config.add_view('crdppf.views.administration.Config', route_name='configpanel')
    config.add_view('crdppf.views.administration.Config', route_name='formulaire_reglements')

    config.add_route('catchall_static', '/*subpath')
    config.add_view('crdppf.static.static_view', route_name='catchall_static')
    
    config.scan()


