# -*- coding: UTF-8 -*-
from pyramid.view import view_config

from simplejson import loads as sloads

from crdppf.models import DBSession
from crdppf.models import Topics, Documents, LegalDocuments
from crdppf.models import Town

@view_config(route_name='getTownList', renderer='json')
def getTownList(request):
    """ Loads the list of the cadastres of the Canton."""
    
    results = {}

    if 'numcad' in Town.__table__.columns.keys():
        results = DBSession.query(Town).order_by(Town.numcad.asc()).all()
    else:
        results = DBSession.query(Town).order_by(Town.numcom.asc()).all()

    towns = []
    for town in results :
        if 'numcad' in Town.__table__.columns.keys():
            numcad = town.numcad
            cadnom = town.cadnom
        else:
            numcad = None
            cadnom = None

        towns.append({
            'idobj': town.idobj,
            'numcom': town.numcom,
            'comnom': town.comnom,
            'numcad': numcad,
            'cadnom': cadnom,
            'nufeco': town.nufeco
        })

    return towns

@view_config(route_name='getTopicsList', renderer='json')
def getTopicsList(request):
    """ Loads the list of the topics."""
    
    results = {}
    results = DBSession.query(Topics).order_by(Topics.topicid.asc()).all()

    topics = []
    for topic in results :
        topics.append({
            'topicid':topic.topicid, 
            'topicname':topic.topicname, 
            'authorityfk':topic.authorityfk, 
            #'publicationdate':topic.publicationdate.isoformat(), 
            'topicorder':topic.topicorder
        })

    return topics

@view_config(route_name='createNewDocEntry', renderer='json')
def createNewDocEntry(request):
    # Attention il faut que l'utilisateur puisse écrire dans la table et d'1, mais aussi qu'il ait le droit sur la SEQUENCE dans PG
    data = sloads(request.POST['data'])
    
    document = Documents()
    
    if data['numcom']:
        document.nocom = int(data['numcom'])
    else:
        document.nocom = None
    if data['nufeco']:
        document.nufeco = int(data['nufeco'])
    else:
        document.nufeco = None
    if data['numcad']:    
        document.nocad = int(data['numcad'])
    else:
        document.nocad = None
    document.nomcom = data['comnom']
    document.doctype = data['doctype']
    document.topicfk = data['topicfk']
    document.titre = data['titre']
    document.titreofficiel = data['titreofficiel']
    document.abreviation = data['abreviation']
    document.noofficiel = data['noofficiel']
    document.url = data['url']
    document.statutjuridique = data['statutjuridique']
    if data['datesanction']:
        document.datesanction = data['datesanction']
    else:
        document.datesanction = None
    if data['dateabrogation']:
        document.dateabrogation = data['dateabrogation']
    else:
        document.dateabrogation = None
    document.operateursaisie = data['operateursaisie']
    if data['datesaisie']:
        document.datesaisie = data['datesaisie']
    else:
        document.datesaisie = None
    document.canton = data['canton']

    DBSession.add(document)

    DBSession.flush()

    return {'success':True}

@view_config(route_name='getLegalDocuments', renderer='json')
def getLegalDocuments(request, filters):
    """Gets all the legal documents related to a feature.
    """
    doclist = []
    documents = {}
    
    #~ sdf
    #~ if filters is not None:
        #~ for key in filters.keys():
            #~ documents = DBSession.query(LegalDocuments).filter_by(key=filters['key']).all()
    #~ else:
    documents = DBSession.query(LegalDocuments).order_by(LegalDocuments.docid.asc()).all()

    for document in documents :
        doclist.append({
            'documentid':document.docid,
            'doctype':document.doctype,
            'lang':document.lang,
            'state':document.state,
            'chmunicipalitynb':document.chmunicipalitynb, 
            'municipalitynb':document.municipalitynb, 
            'municipalityname':document.municipalityname, 
            'cadastrenb':document.cadastrenb, 
            'title':document.title, 
            'officialtitle':document.officialtitle, 
            'abbreviation':document.abbreviation, 
            'officialnb':document.officialnb,
            'legalstate':document.legalstate,
            'remoteurl':document.remoteurl,
            'localurl':document.localurl,
            'sanctiondate':document.sanctiondate.isoformat() if document.sanctiondate else None,
            'abolishingdate':document.abolishingdate.isoformat() if document.abolishingdate else None,
            'entrydate':document.entrydate.isoformat() if document.entrydate else None,
            'publicationdate':document.publicationdate.isoformat() if document.publicationdate else None,
            #'revisiondate':document.revisiondate.isoformat() if document.revisiondate else None,
            'operator':document.operator
        })
        
    return {'docs': doclist}