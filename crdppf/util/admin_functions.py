# -*- coding: UTF-8 -*-
from pyramid.view import view_config
#
from simplejson import loads
# import types

from crdppf.models import DBSession
from crdppf.models.models import Translations


@view_config(route_name='get_translations_list', renderer='json')
def get_translations_list(request):
    """Loads the translations for all the multilingual labels
    """
    try:
        limit = int(request.params['limit'])
        start = int(request.params['start'])
    except:
        limit = 25
        start = 0

    if request.params['sort'] == 'id':
        sort = 'Translations.id'
    else:
        sort = request.params['sort']
    sort += ' '+request.params['dir']

    filter_params = {}

    try:
        filter_params = request.params['filter']
        filter_params = loads(filter_params)
    except KeyError:
        filter_params = None

    if filter_params is None:
        totalCount = int(DBSession.query(Translations).count())
    else:
        totalCount = '999'
    translationslist = DBSession.query(Translations).order_by(Translations.id).offset(start).limit(limit).first()
    if translationslist:
        translationslist = translationslist  # just for flake8 to stop complaining

    #  if filter_params is not None :
    #      for filterparam in filter_params :
    #          if filterparam['type'] == 'numeric':
    #              if filterparam['field'] == 'id_user':
    #                  filterparam['field'] = '\"order\".id_user'
    #              if filterparam['comparison'] == 'eq':
    #                  filter = str(filterparam['field'])+'='+str(filterparam['value'])
    #              elif filterparam['comparison'] == 'lt':
    #                  filter = str(filterparam['field'])+'<'+str(filterparam['value'])
    #              elif filterparam['comparison'] == 'gt' :
    #                  filter = str(filterparam['field'])+'>'+str(filterparam['value'])
    #              orderlist = orderlist.filter(filter)
    #          if filterparam['type'] == 'date':
    #              if filterparam['comparison'] == 'eq':
    #                  filter = str(filterparam['field'])+'=\''+filterparam['value']+'\''
    #              elif filterparam['comparison'] == 'lt':
    #                  filter = str(filterparam['field'])+'<\''+str(filterparam['value'])+'\''
    #              elif filterparam['comparison'] == 'gt' :
    #                  filter = str(filterparam['field'])+'>\''+str(filterparam['value'])+'\''
    #              orderlist = orderlist.filter(filter)
    #          elif filterparam['type'] == 'string':
    #              orderlist = orderlist.filter(getattr(Order, filterparam['field']).like("%%%s%%" % filterparam['value']))
    #          elif filterparam['type'] == 'boolean':
    #              filter = str(filterparam['field'])+'='+str(filterparam['value'])
    #              orderlist = orderlist.filter(filter)
    #          elif filterparam['type'] == 'list':
    #              for option in filterparam['value']:
    #                  filter = str(filterparam['field']) + '=\'' + str(option) +'\''
    #                  orderlist = orderlist.filter(filter)
    #      orderlist = orderlist.order_by(sort).offset(start).limit(limit)
    #  else :
    #      orderlist =sessionDB.query(Order).order_by(sort).offset(start).limit(limit).all()

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

    translations = {
        'translations': list,
        'totalCount': totalCount
    }

    return translations

#  def get_translations_list(request):
#      session = request.session
#      try:
#          session['role']
#      except KeyError :
#          return HTTPForbidden()
#      if int(session['role']) != 1 or session['login'] == False:
#          return HTTPForbidden()
#      sessionDB = DBSession()
#      limit = int(request.params['limit'])
#      start = int(request.params['start'])
#      status =''
#      try:
#          status =  int(request.params['order_state'])
#      except:
#          status = None
#          pass
#      if request.params['sort'] == "id_user":
#          sort = "\"order\".id_user"
#      else:
#          sort = request.params['sort']
#      sort += ' '+request.params['dir']
#      filter = ''
#      filter_params = {}

#      try:
#          filter_params = request.params['filter']
#          filter_params = simplejson.loads(filter_params)
#      except KeyError:
#          filter_params = None

#      if status is None:
#          totalCount =  int(sessionDB.query(Order).count())
#      else:
#          totalCount =  int(sessionDB.query(Order).filter(Order.order_state==0).count())
#      orderlist = sessionDB.query(Order)

#      if status == 0 and filter_params is not None:
#          filter_params.append({u'comparison': u'eq', u'type': u'numeric', u'value': 0, u'field': u'order_state'})
#      elif status == 0 :
#          filter_params=[{u'comparison': u'eq', u'type': u'numeric', u'value': 0, u'field': u'order_state'}]
#          #orderlist = orderlist.filter('order_state=0')

#      if filter_params is not None :
#          for filterparam in filter_params :
#              if filterparam['type'] == 'numeric':
#                  if filterparam['field'] == 'id_user':
#                      filterparam['field'] = '\"order\".id_user'
#                  if filterparam['comparison'] == 'eq':
#                      filter = str(filterparam['field'])+'='+str(filterparam['value'])
#                  elif filterparam['comparison'] == 'lt':
#                      filter = str(filterparam['field'])+'<'+str(filterparam['value'])
#                  elif filterparam['comparison'] == 'gt' :
#                      filter = str(filterparam['field'])+'>'+str(filterparam['value'])
#                  orderlist = orderlist.filter(filter)
#              if filterparam['type'] == 'date':
#                  if filterparam['comparison'] == 'eq':
#                      filter = str(filterparam['field'])+'=\''+filterparam['value']+'\''
#                  elif filterparam['comparison'] == 'lt':
#                      filter = str(filterparam['field'])+'<\''+str(filterparam['value'])+'\''
#                  elif filterparam['comparison'] == 'gt' :
#                      filter = str(filterparam['field'])+'>\''+str(filterparam['value'])+'\''
#                  orderlist = orderlist.filter(filter)
#              elif filterparam['type'] == 'string':
#                  orderlist = orderlist.filter(getattr(Order, filterparam['field']).like("%%%s%%" % filterparam['value']))
#              elif filterparam['type'] == 'boolean':
#                  filter = str(filterparam['field'])+'='+str(filterparam['value'])
#                  orderlist = orderlist.filter(filter)
#              elif filterparam['type'] == 'list':
#                  for option in filterparam['value']:
#                      filter = str(filterparam['field']) + '=\'' + str(option) +'\''
#                      orderlist = orderlist.filter(filter)
#          orderlist = orderlist.order_by(sort).offset(start).limit(limit)
#      else :
#          orderlist =sessionDB.query(Order).order_by(sort).offset(start).limit(limit).all()

#      result = list()

#      json= simplejson.dumps(result2)
#      return Response(json,content_type='application/json; charset=utf-8')
