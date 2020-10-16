from sqlalchemy import(
    Column,
    Integer,
    String,
    ForeignKey)

from sqlalchemy.orm import relationship, backref

from papyrus.geo_interface import GeoInterface

from geoalchemy2 import Geometry

from crdppf import db_config

srid_ = db_config['srid']

from crdppf.models import Base


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


class Informations(Base):
    __tablename__ = 'informations'
    __table_args__ = {'schema': db_config['schema'], 'autoload': True}


class ExclusionsResponsabilite(Base):
    __tablename__ = 'exclusions_responsabilite'
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
        srfmai = Column(table_def_['att_property_area'], String)
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

if 'land_use_plans_primary_use' in db_config['restrictions']:
    table_def_ = db_config['tables']['land_use_plans_primary_use']

    class PrimaryLandUseZones(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class PrimaryLandUseZones():
        pass

if 'land_use_plans_overlay_zones' in db_config['restrictions']:
    table_def_ = db_config['tables']['land_use_plans_overlay_zones']

    class SecondaryLandUseZones(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class SecondaryLandUseZones():
        pass

if 'land_use_plans_overlay_perimeters' in db_config['restrictions']:
    table_def_ = db_config['tables']['land_use_plans_overlay_perimeters']

    class ComplementaryLandUsePerimeters(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class ComplementaryLandUsePerimeters():
        pass

if 'land_use_plans_linear_constraints' in db_config['restrictions']:
    table_def_ = db_config['tables']['land_use_plans_linear_constraints']

    class LandUseLinearConstraints(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("MULTILINE", srid=srid_))
else:
    class LandUseLinearConstraints():
        pass

if 'land_use_plans_point_constraints' in db_config['restrictions']:
    table_def_ = db_config['tables']['land_use_plans_point_constraints']

    class LandUsePointConstraints(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("POINT", srid=srid_))
else:
    class LandUsePointConstraints():
        pass

# models for the topic national roads
if 'motorways_project_planing_zones' in db_config['restrictions']:
    table_def_ = db_config['tables']['motorways_project_planing_zones']

    class CHHighwaysProjectZones(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class CHHighwaysProjectZones():
        pass

if 'motorways_building_lines' in db_config['restrictions']:
    table_def_ = db_config['tables']['motorways_building_lines']

    class CHHighwaysConstructionLimits(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class CHHighwaysConstructionLimits():
        pass

# models for the national railways
if 'railways_project_planning_zones' in db_config['restrictions']:
    table_def_ = db_config['tables']['railways_project_planning_zones']

    class CHRailwaysProjectZones(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class CHRailwaysProjectZones():
        pass

if 'railways_building_lines' in db_config['restrictions']:
    table_def_ = db_config['tables']['railways_building_lines']

    class CHRailwaysConstructionLimits(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class CHRailwaysConstructionLimits():
        pass

# models for airports
if 'airports_security_zone_plans' in db_config['restrictions']:
    table_def_ = db_config['tables']['airports_security_zone_plans']

    class CHAirportSecurityZones(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
        # ch.bazl.sicherheitszonenplan.oereb
else:
    class CHAirportSecurityZones():
        pass

if 'airports_project_planning_zones' in db_config['restrictions']:
    table_def_ = db_config['tables']['airports_project_planning_zones']

    class CHAirportProjectZones(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
        # ch.bazl.projektierungszonen-flughafenanlagen.oereb
else:
    class CHAirportProjectZones():
        pass


if 'airports_building_lines' in db_config['restrictions']:
    table_def_ = db_config['tables']['airports_building_lines']

    class CHAirportConstructionLimits(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
        # ch.bazl.projektierungszonen-flughafenanlagen.oereb
else:
    class CHAirportConstructionLimits():
        pass


# models for theme: register of polluted sites
if 'contaminated_sites' in db_config['restrictions']:
    table_def_ = db_config['tables']['contaminated_sites']

    class PollutedSites(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class PollutedSites():
        pass

if 'contaminated_military_sites' in db_config['restrictions']:
    table_def_ = db_config['tables']['contaminated_military_sites']

    class ContaminatedMilitarySites(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(String, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class ContaminatedMilitarySites():
        pass


if 'contaminated_civil_aviation_sites' in db_config['restrictions']:
    table_def_ = db_config['tables']['contaminated_civil_aviation_sites']

    class CHPollutedSitesCivilAirports(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class CHPollutedSitesCivilAirports():
        pass


if 'contaminated_public_transport_sites' in db_config['restrictions']:
    table_def_ = db_config['tables']['contaminated_public_transport_sites']

    class CHPollutedSitesPublicTransports(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
        # ch.bav.kataster-belasteter-standorte-oev.oereb
else:
    class CHPollutedSitesPublicTransports():
        pass

# models for the topic noise
if 'road_noise' in db_config['restrictions']:
    table_def_ = db_config['tables']['noise_sensitivity_levels']

    class RoadNoise(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class RoadNoise():
        pass

# models for water protection
if 'groundwater_protection_zones' in db_config['restrictions']:
    table_def_ = db_config['tables']['groundwater_protection_zones']
    class WaterProtectionZones(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(String(40), primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class WaterProtectionZones():
        pass

if 'groundwater_protection_sites' in db_config['restrictions']:
    table_def_ = db_config['tables']['groundwater_protection_sites']

    class WaterProtectionPerimeters(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(String(40), primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class WaterProtectionPerimeters():
        pass

# models for the topic Forest
if 'forest_perimeters' in db_config['restrictions']:
    table_def_ = db_config['tables']['forest_perimeters']

    class ForestLimits(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class ForestLimits():
        pass

if 'forest_distance_lines' in db_config['restrictions']:
    table_def_ = db_config['tables']['forest_distance_lines']

    class ForestDistances(GeoInterface, Base):
        __tablename__ = table_def_['tablename']
        __table_args__ = {'schema': table_def_['schema'], 'autoload': True}
        idobj = Column(Integer, primary_key=True)
        geom = Column(Geometry("GEOMETRY", srid=srid_))
else:
    class ForestDistances():
        pass

# STOP models used for GetFeature queries
