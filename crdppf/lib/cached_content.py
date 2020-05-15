# -*- coding: UTF-8 -*-

from dogpile.cache.region import make_region

cache_region = make_region()
cache_region.configure("dogpile.cache.memory")

from crdppf.models import DBSession

from crdppf.models.models import AppConfig, Translations, Glossar
from crdppf.models.models import Informations, ExclusionsResponsabilite

import logging

log = logging.getLogger(__name__)


@cache_region.cache_on_arguments()
def get_cached_content(request):

    d = {}

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

    d = {}

    # First get all the translated strings for the selected language
    translations = DBSession.query(Translations).all()

    for translation in translations:

        if getattr(translation, lang):
            d[str(translation.varstr)] = getattr(translation, lang)
        else:
            log.warning("There is a undefined translation")
            d[str(translation.varstr)] = u'undefined'

    # TODO : Try to get this working, as it seems that MFP has issues
    # with multiple table/datasources!

    # Second get all the complemtary informations for the TOC
    #    infos = DBSession.query(Informations).filter_by(lang=lang).all()

    #    informations = []
    #    for information in infos:
    #        if not information.contenu == '':
    #            informations.append([
    #                information.titre, information.contenu
    #            ])
    #        else:
    #            log.warning("There is a empty information element")

    #    d["informations"] = {
    #            "columns": ["titre", "contenu"],
    #            "data": informations
    #        }

    # Third get all the disclaimers for the different topics
    disclaimers = DBSession.query(ExclusionsResponsabilite).filter_by(lang=lang).all()

    exclusions = []
    for disclaimer in disclaimers:
        if not disclaimer.contenu == '':
            exclusions.append([
                disclaimer.titre, disclaimer.contenu
            ])
        else:
            log.warning("There is a empty disclaimer element")

    d["disclaimers"] = {
            "columns": ["titre", "contenu"],
            "data": exclusions
        }

    # Fourth get all the definitions for the selected language
    glossar = DBSession.query(Glossar).filter_by(lang=lang).all()

    abbreviations = []
    for term in glossar:
        if not term.expression == '' or term.definition == '':
            abbreviations.append([
                term.expression, term.definition
            ])
        else:
            log.warning("There is a empty definition")

    d["glossar"] = [{
        "glossarlabel": d["pdfGlossarLabel"],
        "definitions": {
            "columns": ["term", "definition"],
            "data": abbreviations
        }
    }]

    return d
