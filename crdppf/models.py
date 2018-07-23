from sqlalchemy import(
    Column,
    Integer,
    String,
    ForeignKey)

from sqlalchemy.orm import relationship, backref

import sqlahelper

DBSession = sqlahelper.get_session()

from papyrus.geo_interface import GeoInterface

from geoalchemy2 import Geometry

from crdppf import db_config

srid_ = db_config['srid']

Base = sqlahelper.get_base()


# Models for the configuration of the application
class AppConfig(Base):
    __tablename__ = 'appconfig'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}


# START models used for static extraction and general models
class Topics(Base):
    __tablename__ = 'topics'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    layers = relationship("Layers", backref=backref("layers"), lazy="joined")
    authorityfk = Column(Integer, ForeignKey('crdppf.authority.authorityid'))
    authority = relationship("Authority", backref=backref("authority"), lazy="joined")


class Layers(Base):
    __tablename__ = 'layers'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    topicfk = Column(String, ForeignKey('crdppf.topics.topicid'))
    topic = relationship("Topics", backref=backref("topic"), lazy="joined")


class Documents(Base):
    __tablename__ = 'documents_edition'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    legalstate = Column(Integer, ForeignKey('crdppf.vl_legalstate.id'))
    legalstates = relationship("Legalstates", lazy="joined")
    doctype = Column(Integer, ForeignKey('crdppf.vl_doctype.id'))
    doctypes = relationship("DocumentType", lazy="joined")


class OriginReference(Base):
    __tablename__ = 'origin_reference'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    docid = Column(String, ForeignKey('crdppf.documents.docid'))


class LegalDocuments(Base):
    __tablename__ = 'documents'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    docid = Column(String, primary_key=True)
    legalstate = Column(Integer, ForeignKey('crdppf.vl_legalstate.id'))
    legalstates = relationship("Legalstates", lazy="joined")
    doctype = Column(Integer, ForeignKey('crdppf.vl_doctype.id'))
    doctypes = relationship("DocumentType", lazy="joined")
    origins = relationship("OriginReference", backref="documents", lazy="joined")


class Legalstates(Base):
    __tablename__ = 'vl_legalstate'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}


class DocumentType(Base):
    __tablename__ = 'vl_doctype'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}


class Authority(Base):
    __tablename__ = 'authority'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}


class PaperFormats(Base):
    __tablename__ = 'paperformats'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}


class Themes(Base):
    __tablename__ = 'themes'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}


class Translations(Base):
    __tablename__ = 'translations'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}


class Glossar(Base):
    __tablename__ = 'glossar'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}

# DATA SECTION
if 'town' in db_config['tables']:
    table_def_ = db_config['tables']['town']
    if 'att_cadastre_number' in table_def_:
        class Town(GeoInterface, Base):
            __tablename__ = table_def_['tablename']
            __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
            idobj = Column(table_def_['att_id'], Integer, primary_key=True)
            numcad = Column(table_def_['att_cadastre_number'], Integer)
            numcom = Column(table_def_['att_commune_number'], Integer)
            comnom = Column(table_def_['att_commune_name'], String)
            cadnom = Column(table_def_['att_cadastre_name'], String)
            nufeco = Column(table_def_['att_federal_number'], Integer)
            geom = Column(Geometry("GEOMETRY", srid=srid_))
    else:
        class Town(GeoInterface, Base):
            __tablename__ = table_def_['tablename']
            __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
            idobj = Column(table_def_['att_id'], Integer, primary_key=True)
            numcom = Column(table_def_['att_commune_number'], Integer)
            comnom = Column(table_def_['att_commune_name'], String)
            nufeco = Column(table_def_['att_federal_number'], Integer)
            geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class Town():
        fake_attr = True

if 'property' in db_config['tables']:
    table_def_ = db_config['tables']['property']

    class Property(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        noobj = Column(table_def_['att_id'], Integer, primary_key=True)
        id = Column(table_def_['att_id_property'], String)
        egrid = Column(table_def_['att_egrid'], String)
        nummai = Column(table_def_['att_property_number'], String)
        typimm = Column(table_def_['att_property_type'], String)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class Property():
        pass

if 'local_names' in db_config['tables']:
    table_def_ = db_config['tables']['local_names']

    class LocalName(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idcnlo = Column(table_def_['att_id'], String, primary_key=True)
        nomloc = Column(table_def_['att_local_name'], String)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class LocalName():
        pass
# STOP models used for static extraction and general models


# START models used for GetFeature queries
# models for theme: allocation plan
class PrimaryLandUseZones(GeoInterface, Base):
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    __tablename__ = 'r73_affectations_primaires'
    idobj = Column(Integer, primary_key=True)
    geom = Column(Geometry("GEOMETRY", srid=srid_))


class SecondaryLandUseZones(GeoInterface, Base):
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    __tablename__ = 'r73_zones_superposees'
    idobj = Column(Integer, primary_key=True)
    geom = Column(Geometry("GEOMETRY", srid=srid_))


class ComplementaryLandUsePerimeters(GeoInterface, Base):
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    __tablename__ = 'r73_perimetres_superposes'
    idobj = Column(Integer, primary_key=True)
    geom = Column(Geometry("GEOMETRY", srid=srid_))


class LandUseLinearConstraints(GeoInterface, Base):
    __tablename__ = 'r73_contenus_lineaires'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    idobj = Column(Integer, primary_key=True)
    geom = Column(Geometry("MULTILINE", srid=srid_))


class LandUsePointConstraints(GeoInterface, Base):
    __tablename__ = 'r73_contenus_ponctuels'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    idobj = Column(Integer, primary_key=True)
    geom = Column(Geometry("POINT", srid=srid_))

# models for the topic national roads

if 'highways_project_zones' in db_config['restrictions']:
    class CHHighwaysProjectZones(GeoInterface, Base):
        __tablename__ = 'r87_astra_projektierungszonen_nationalstrassen'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class CHHighwaysProjectZones():
        pass

if 'highways_construction_limits' in db_config['restrictions']:
    class CHHighwaysConstructionLimits(GeoInterface, Base):
        __tablename__ = 'r88_astra_baulinien_nationalstrassen'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class CHHighwaysConstructionLimits():
        pass

# models for the national railways

if 'railways_project_zones' in db_config['restrictions']:
    class CHRailwaysProjectZones(GeoInterface, Base):
        __tablename__ = 'r96_bav_projektierungszonen_eisenbahnanlagen'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class CHRailwaysProjectZones():
        pass

if 'railways_construction_limits' in db_config['restrictions']:
    class CHRailwaysConstructionLimits(GeoInterface, Base):
        __tablename__ = 'r97_bav_baulinien_eisenbahnanlagen'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class CHRailwaysConstructionLimits():
        pass

# models for airports
if 'airport_security_zones' in db_config['restrictions']:
    class CHAirportSecurityZones(GeoInterface, Base):
        __tablename__ = 'r108_bazl_sicherheitszonenplan'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))

    class CHAirportSecurityZonesPDF(GeoInterface, Base):
        __tablename__ = 'r108_bazl_sicherheitszonenplan_pdf'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
        # ch.bazl.sicherheitszonenplan.oereb
else:
    class CHAirportSecurityZones():
        pass

    class CHAirportSecurityZonesPDF():
        pass

if 'airport_project_zones' in db_config['restrictions']:
    class CHAirportProjectZones(GeoInterface, Base):
        __tablename__ = 'r103_bazl_projektierungszonen_flughafenanlagen'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))

    class CHAirportProjectZonesPDF(GeoInterface, Base):
        __tablename__ = 'r103_bazl_projektierungszonen_flughafenanlagen_pdf'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
        # ch.bazl.projektierungszonen-flughafenanlagen.oereb

else:
    class CHAirportProjectZones():
        pass

    class CHAirportProjectZonesPDF():
        pass

if 'airport_construction_limits' in db_config['restrictions']:
    class CHAirportConstructionLimits(GeoInterface, Base):
        __tablename__ = 'r104_bazl_baulinien_flughafenanlagen'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))

    class CHAirportConstructionLimitsPDF(GeoInterface, Base):
        __tablename__ = 'r104_bazl_baulinien_flughafenanlagen_pdf'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
        # ch.bazl.projektierungszonen-flughafenanlagen.oereb

else:
    class CHAirportConstructionLimits():
        pass

    class CHAirportConstructionLimitsPDF():
        pass


# models for theme: register of polluted sites
class PollutedSites(GeoInterface, Base):
    __tablename__ = 'r116_sites_pollues'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    idobj = Column(Integer, primary_key=True)
    geom = Column(Geometry("GEOMETRY", srid=srid_))

if 'airport_polluted_sites' in db_config['restrictions']:
    class CHPollutedSitesCivilAirports(GeoInterface, Base):
        __tablename__ = 'r118_bazl_belastete_standorte_zivilflugplaetze'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))

    class CHPollutedSitesCivilAirportsPDF(GeoInterface, Base):
        __tablename__ = 'r118_bazl_belastete_standorte_zivilflugplaetze_pdf'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))

else:
    class CHPollutedSitesCivilAirports():
        pass

    class CHPollutedSitesCivilAirportsPDF():
        pass

if 'transportation_polluted_sites' in db_config['restrictions']:
    class CHPollutedSitesPublicTransports(GeoInterface, Base):
        __tablename__ = 'r119_bav_belastete_standorte_oev'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))

    class CHPollutedSitesPublicTransportsPDF(GeoInterface, Base):
        __tablename__ = 'r119_bav_belastete_standorte_oev_pdf'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))

    # ch.bav.kataster-belasteter-standorte-oev.oereb
else:
    class CHPollutedSitesPublicTransports():
        pass

    class CHPollutedSitesPublicTransportsPDF():
        pass
# models for the topic noise

if 'road_noise' in db_config['restrictions']:
    class RoadNoise(GeoInterface, Base):
        __tablename__ = 'r145_sens_bruit'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class RoadNoise():
        pass


# models for water protection
class WaterProtectionZones(GeoInterface, Base):
    __tablename__ = 'r131_zone_prot_eau'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    idobj = Column(String(40), primary_key=True)
    geom = Column(Geometry("GEOMETRY", srid=srid_))


class WaterProtectionPerimeters(GeoInterface, Base):
    __tablename__ = 'r132_perimetre_prot_eau'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}
    idobj = Column(String(40), primary_key=True)
    geom = Column(Geometry("GEOMETRY", srid=srid_))

# models for the topic Forest
if 'forest_limits' in db_config['restrictions']:
    class ForestLimits(GeoInterface, Base):
        __tablename__ = 'r157_lim_foret'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class ForestLimits():
        pass

if 'forest_distances' in db_config['restrictions']:
    class ForestDistances(GeoInterface, Base):
        __tablename__ = 'r159_dist_foret'
        __table_args__ = {'schema': db_config['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class ForestDistances():
        pass

# STOP models used for GetFeature queries
