# -*- coding: utf-8 -*-

import sqlalchemy.orm as orm
from sqlalchemy.ext.declarative import declarative_base
from zope.sqlalchemy import register

# CREATE PostgreSQL Session and base
maker = orm.sessionmaker(autoflush=True, autocommit=False)
register(maker)
DBSession = orm.scoped_session(maker)

Base = declarative_base()

metadata = Base.metadata

def init_model(engine):
    """Call me before using any of the tables or classes in the model."""

    DBSession.configure(bind=engine)
    metadata.bind = engine
