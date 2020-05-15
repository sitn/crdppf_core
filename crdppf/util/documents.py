# -*- coding: UTF-8 -*-

from sqlalchemy import or_

from crdppf.models import DBSession
from crdppf.models.models import LegalDocuments, OriginReference


def get_documents(filters=None):
    """
        Gets all the legal documents related to a feature.
    """
    doclist = []
    documents = {}

    if filters:
        documents = DBSession.query(LegalDocuments).filter(
            LegalDocuments.docid.in_(filters['docids'])
        )
        if 'cadastrenb' in filters.keys():
            documents = documents.filter(or_(
                LegalDocuments.cadastrenb == None,
                LegalDocuments.cadastrenb == filters['cadastrenb']
            )).order_by(LegalDocuments.doctype.asc())
        if 'chmunicipalitynb' in filters.keys():
            documents = documents.filter(or_(
                LegalDocuments.chmunicipalitynb == filters['chmunicipalitynb'],
                LegalDocuments.chmunicipalitynb == None
            )).order_by(LegalDocuments.doctype.asc())
    else:
        documents = DBSession.query(LegalDocuments).order_by(
            LegalDocuments.doctype.asc()
        ).order_by(
            LegalDocuments.state.asc()
        ).order_by(
            LegalDocuments.chmunicipalitynb.asc()
        ).order_by(
            LegalDocuments.cadastrenb.asc()
        )

    documents = documents.order_by(
        LegalDocuments.doctype.asc()
    ).order_by(
        LegalDocuments.state.asc()
    ).order_by(
        LegalDocuments.chmunicipalitynb.asc()
    ).order_by(
        LegalDocuments.cadastrenb.asc()
    ).all()

    for document in documents:
        origins = []
        for origin in document.origins:
            origins.append(origin.fkobj)
        doclist.append({
            'documentid': document.docid,
            'doctype': document.doctypes.value,
            'lang': document.lang,
            'state': document.state,
            'chmunicipalitynb': document.chmunicipalitynb,
            'municipalitynb': document.municipalitynb,
            'municipalityname': document.municipalityname,
            'cadastrenb': document.cadastrenb,
            'title': document.title,
            'officialtitle': document.officialtitle,
            'abbreviation': document.abbreviation,
            'officialnb': document.officialnb,
            'legalstate': document.legalstates.value,
            'remoteurl': document.remoteurl,
            'localurl': document.localurl,
            'sanctiondate': document.sanctiondate.isoformat()
            if document.sanctiondate else None,
            'abolishingdate': document.abolishingdate.isoformat()
            if document.abolishingdate else None,
            'entrydate': document.entrydate.isoformat()
            if document.entrydate else None,
            'publicationdate': document.publicationdate.isoformat()
            if document.publicationdate else None,
            'revisiondate': document.revisiondate.isoformat()
            if document.revisiondate else None,
            'operator': document.operator,
            'origins': origins
        })

    return doclist


def get_document_ref(docfilters=None):
    """
        Gets all the id's of the documents referenced by an object, layer,
        topic or document.
    """
    referenceslist = set()
    rereferenceslist = set()

    if docfilters:
        for filtercriteria in docfilters:

            references = DBSession.query(OriginReference).filter_by(
                fkobj=filtercriteria
            ).all()

            if references is not None:
                for reference in references:
                    referenceslist.add(reference.docid)
    else:
        references = DBSession.query(OriginReference).all()
        for reference in references:
            referenceslist.add(reference.docid)

    # check if a referenced document references an other one
    if referenceslist is not None:
        for reference in referenceslist:

            rereferences = DBSession.query(OriginReference).filter_by(
                fkobj=str(reference)
            ).all()

            if rereferences is not None:
                for rereference in rereferences:
                    rereferenceslist.add(rereference.docid)

    if rereferenceslist is not None:
        for rereference in rereferenceslist:
            if rereference not in referenceslist:
                referenceslist.add(rereference)

    return referenceslist
