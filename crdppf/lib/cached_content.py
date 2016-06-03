
from dogpile.cache.region import make_region

cache_region = make_region()
cache_region.configure("dogpile.cache.memory")

from crdppf.models import DBSession

from crdppf.models import AppConfig, Translations

import logging

log = logging.getLogger(__name__)

@cache_region.cache_on_arguments()
def get_cached_content(request):

    d={}

    canton_logo = DBSession.query(AppConfig).filter_by(parameter='cantonlogopath').first()
    ch_logo = DBSession.query(AppConfig).filter_by(parameter='CHlogopath').first()
    crdppf_logo = DBSession.query(AppConfig).filter_by(parameter='crdppflogopath').first()

    d['canton_logo'] = '/'.join([
        request.registry.settings['localhost_url'],
        'proj/images',
        canton_logo.paramvalue
    ])
    
    d['ch_logo'] = '/'.join([
        request.registry.settings['localhost_url'],
        'proj/images',
        ch_logo.paramvalue
    ])
    
    d['crdppf_logo'] = '/'.join([
        request.registry.settings['localhost_url'],
        'proj/images',
        crdppf_logo.paramvalue
    ])

    return d

@cache_region.cache_on_arguments()
def get_cached_content_l10n(lang):

    d={}

    translations = DBSession.query(Translations).all()

    for translation in translations:

        if  getattr(translation, lang):
            d[str(translation.varstr)] = getattr(translation, lang)
        else:
            log.warning("There is a undefined translation")
    #~ sdf
    return d
