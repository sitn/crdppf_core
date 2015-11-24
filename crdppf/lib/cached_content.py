
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

    translations_list = {
        'legendlabel': 'legend_header_label',
        'completlegendlabel': 'full_topic_legend_label',
        'teneur': 'tenor_label',
        'legalbaseslabel': 'legal_base_label',
        'legalprovisionslabel': 'legal_disposition_label',
        'referenceslabel': 'reference_label',
        'competentauthoritylabel': 'authority_label',
        'temporaryprovisionslabel': 'transitory_disposition_label',
        'mapslabel': 'maps_label',
        'otherslabel': 'other_label',
    }

    translations = DBSession.query(Translations).filter(Translations.varstr.in_(translations_list)).all()

    for translation in translations:

        varstr = translation.varstr

        if  getattr(translation, lang):
            d[translations_list[varstr]] = getattr(translation, lang)
        else:
            log.warning("There is a undefined translation")

    return d
