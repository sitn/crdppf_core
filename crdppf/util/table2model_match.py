# -*- coding: UTF-8 -*-
from pyramid.view import view_config
from crdppf.models import DBSession, Table2model 

#@view_config(route_name='table2model_match', renderer='json') 
def table2model_match(layername):
    """Associates a PG tablename with a modelname"""
    tables = []
    
    tables = DBSession.query(Table2model).filter(Table2model.layername)all()
    sdf

    return model