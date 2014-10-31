# -*- coding: UTF-8 -*-
from pyramid.view import view_config
from pyramid.response import Response

import types

from crdppf.models import DBSession, Translations

@view_config(route_name='get_translations_list', renderer='json')
def get_translations_list(request):
    """Loads the translations for all the multilingual labels
    """
    limit = int(request.params['limit'])
    start = int(request.params['start'])
    
    if request.params['sort'] == 'id':
        sort = 'Translations.Id'
    else:
        sort = request.params['sort']
    sort += ' '+request.params['dir']
    filter =  None
    filter_params = {}

    try:
        filter_params = request.params['filter']
        filter_params = simplejson.loads(filter_params)
    except KeyError: 
        filter_params = None

    if filter_params is None:
        totalCount =  int(DBSession.query(Translations).count())
    else:
        totalCount =  '999'
    translationslist = DBSession.query(Translations).order_by(Translations.Id).offset(start).limit(limit).all()

    #~ if filter_params is not None :
        #~ for filterparam in filter_params :
            #~ if filterparam['type'] == 'numeric':
                #~ if filterparam['field'] == 'id_user':
                    #~ filterparam['field'] = '\"order\".id_user'
                #~ if filterparam['comparison'] == 'eq':
                    #~ filter = str(filterparam['field'])+'='+str(filterparam['value'])
                #~ elif filterparam['comparison'] == 'lt':
                    #~ filter = str(filterparam['field'])+'<'+str(filterparam['value'])
                #~ elif filterparam['comparison'] == 'gt' :
                    #~ filter = str(filterparam['field'])+'>'+str(filterparam['value'])
                #~ orderlist = orderlist.filter(filter)
            #~ if filterparam['type'] == 'date':
                #~ if filterparam['comparison'] == 'eq':
                    #~ filter = str(filterparam['field'])+'=\''+filterparam['value']+'\''
                #~ elif filterparam['comparison'] == 'lt':
                    #~ filter = str(filterparam['field'])+'<\''+str(filterparam['value'])+'\''
                #~ elif filterparam['comparison'] == 'gt' :
                    #~ filter = str(filterparam['field'])+'>\''+str(filterparam['value'])+'\''
                #~ orderlist = orderlist.filter(filter)
            #~ elif filterparam['type'] == 'string':
                #~ orderlist = orderlist.filter(getattr(Order, filterparam['field']).like("%%%s%%" % filterparam['value']))
            #~ elif filterparam['type'] == 'boolean':
                #~ filter = str(filterparam['field'])+'='+str(filterparam['value'])
                #~ orderlist = orderlist.filter(filter)
            #~ elif filterparam['type'] == 'list':
                #~ for option in filterparam['value']:
                    #~ filter = str(filterparam['field']) + '=\'' + str(option) +'\''
                    #~ orderlist = orderlist.filter(filter)
        #~ orderlist = orderlist.order_by(sort).offset(start).limit(limit)
    #~ else :
        #~ orderlist =sessionDB.query(Order).order_by(sort).offset(start).limit(limit).all()

    results = DBSession.query(Translations).all()
    list = []
    for result in results:
        list.append({
            'id': result.id,
            'varstr': result.varstr,
            'de': result.de,
            'fr': result.fr,
            'it': result.it,
            'ro': result.ro,
            'en': result.en
        })

    translations={
        'translations': list,
        'totalCount':totalCount
    }

    return translations
    
#~ def get_translations_list(request):
    #~ session = request.session
    #~ try:
        #~ session['role']
    #~ except KeyError :
        #~ return HTTPForbidden()
    #~ if int(session['role']) != 1 or session['login'] == False:
        #~ return HTTPForbidden()
    #~ sessionDB = DBSession()
    #~ limit = int(request.params['limit'])
    #~ start = int(request.params['start'])
    #~ status =''
    #~ try:
        #~ status =  int(request.params['order_state'])
    #~ except:
        #~ status = None
        #~ pass
    #~ if request.params['sort'] == "id_user":
        #~ sort = "\"order\".id_user"
    #~ else:
        #~ sort = request.params['sort']
    #~ sort += ' '+request.params['dir']
    #~ filter = ''
    #~ filter_params = {}
    
    #~ try:
        #~ filter_params = request.params['filter']
        #~ filter_params = simplejson.loads(filter_params)
    #~ except KeyError: 
        #~ filter_params = None

    #~ if status is None:
        #~ totalCount =  int(sessionDB.query(Order).count())
    #~ else:
        #~ totalCount =  int(sessionDB.query(Order).filter(Order.order_state==0).count())
    #~ orderlist = sessionDB.query(Order)

    #~ if status == 0 and filter_params is not None:
        #~ filter_params.append({u'comparison': u'eq', u'type': u'numeric', u'value': 0, u'field': u'order_state'})
    #~ elif status == 0 :
        #~ filter_params=[{u'comparison': u'eq', u'type': u'numeric', u'value': 0, u'field': u'order_state'}]      
        #~ #orderlist = orderlist.filter('order_state=0')

    #~ if filter_params is not None :
        #~ for filterparam in filter_params :
            #~ if filterparam['type'] == 'numeric':
                #~ if filterparam['field'] == 'id_user':
                    #~ filterparam['field'] = '\"order\".id_user'
                #~ if filterparam['comparison'] == 'eq':
                    #~ filter = str(filterparam['field'])+'='+str(filterparam['value'])
                #~ elif filterparam['comparison'] == 'lt':
                    #~ filter = str(filterparam['field'])+'<'+str(filterparam['value'])
                #~ elif filterparam['comparison'] == 'gt' :
                    #~ filter = str(filterparam['field'])+'>'+str(filterparam['value'])
                #~ orderlist = orderlist.filter(filter)
            #~ if filterparam['type'] == 'date':
                #~ if filterparam['comparison'] == 'eq':
                    #~ filter = str(filterparam['field'])+'=\''+filterparam['value']+'\''
                #~ elif filterparam['comparison'] == 'lt':
                    #~ filter = str(filterparam['field'])+'<\''+str(filterparam['value'])+'\''
                #~ elif filterparam['comparison'] == 'gt' :
                    #~ filter = str(filterparam['field'])+'>\''+str(filterparam['value'])+'\''
                #~ orderlist = orderlist.filter(filter)
            #~ elif filterparam['type'] == 'string':
                #~ orderlist = orderlist.filter(getattr(Order, filterparam['field']).like("%%%s%%" % filterparam['value']))
            #~ elif filterparam['type'] == 'boolean':
                #~ filter = str(filterparam['field'])+'='+str(filterparam['value'])
                #~ orderlist = orderlist.filter(filter)
            #~ elif filterparam['type'] == 'list':
                #~ for option in filterparam['value']:
                    #~ filter = str(filterparam['field']) + '=\'' + str(option) +'\''
                    #~ orderlist = orderlist.filter(filter)
        #~ orderlist = orderlist.order_by(sort).offset(start).limit(limit)
    #~ else :
        #~ orderlist =sessionDB.query(Order).order_by(sort).offset(start).limit(limit).all()

    #~ result = list()

    #~ for row in orderlist:
        #~ # Check if there are products type like
        #~ products = ast.literal_eval(row.order_products)
        #~ is_mo = ""
        #~ for product in products:
            #~ product_id = product['id']
            #~ is_mensuration = sessionDB.query(Product).get(product_id)
            #~ if is_mensuration:
                #~ is_mensuration = is_mensuration.is_mensuration
            #~ else:
                #~ is_mensuration = False
            #~ if is_mo == "" and is_mensuration:
                #~ is_mo = "Oui"
            #~ if is_mo == "" and is_mensuration is False:
                #~ is_mo = "Non"
            #~ if is_mo == "Non" and is_mensuration:
                #~ is_mo = "Oui/Non"
            #~ if is_mo == "Oui" and is_mensuration is False:
                #~ is_mo = "Oui/Non"
        
        
        #~ if row.invoice_diff:
            #~ str_invoice_diff = "Oui"
        #~ else:
            #~ str_invoice_diff = "Non"
        
        #~ if row.delivery_date is None:
            #~ d={
                #~ 'id_order': row.id_order,
                #~ 'id_order_millis': row.id_order_millis,
                #~ 'mandat_title': row.mandat_title,
                #~ 'order_date': row.order_date.isoformat(),
                #~ 'mandat_info': row.mandat_info,
                #~ 'mandat_type': row.mandat_type,
                #~ 'invoice_diff': str_invoice_diff,
                #~ 'order_products': row.order_products,
                #~ 'order_state': row.order_state,
                #~ 'pdf_name': row.pdf_name,
                #~ 'id_user': row.id_user,
                #~ 'is_mo': is_mo
            #~ }
        #~ else:
            #~ d={
                #~ 'id_order': row.id_order,
                #~ 'id_order_millis': row.id_order_millis,
                #~ 'mandat_title': row.mandat_title,
                #~ 'order_date': row.order_date.isoformat(),
                #~ 'delivery_date': row.delivery_date.isoformat(),
                #~ 'mandat_info': row.mandat_info,
                #~ 'mandat_type': row.mandat_type,
                #~ 'invoice_diff': str_invoice_diff,
                #~ 'order_products': row.order_products,
                #~ 'order_state': row.order_state,
                #~ 'pdf_name': row.pdf_name,
                #~ 'id_user': row.id_user,
                #~ 'is_mo': is_mo
            #~ }
        #~ result.append(d)
    #~ result2={
        #~ 'commandes':result,
        #~ 'totalCount':totalCount
    #~ }
    
    #~ json= simplejson.dumps(result2)
    #~ return Response(json,content_type='application/json; charset=utf-8')