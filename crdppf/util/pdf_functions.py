# -*- coding: UTF-8 -*-

import urllib
import httplib2
from pyramid.httpexceptions import HTTPBadRequest
import types

# geometry related librabries
from shapely.geometry import Point as splPoint, Polygon as splPolygon
from shapely.geometry import MultiPolygon as splMultiPolygon
from geoalchemy2 import functions, WKTElement

from geojson import loads

from xml.dom.minidom import parseString

from crdppf.models import DBSession
from crdppf.models.models import Translations, PaperFormats
from crdppf.models.models import Town, Property, LocalName


def geom_from_coordinates(coords):
    """ Function to convert a list of coordinates in a geometry
    """
    if (len(coords) > 1 and len(coords) % 2 == 0):
        geom = splPolygon(coords)
    elif (len(coords) > 0 and len(coords) % 2 == 0):
        geom = splPoint(coords)
    else:
        geom = None

    return geom


def get_translations(lang):
    """Loads the translations for all the multilingual labels
    """
    locals = {}
    lang_dict = {
        'fr': Translations.fr,
        'de': Translations.de,
        'it': Translations.it,
        'en': Translations.en
    }
    translations = DBSession.query(Translations.varstr, lang_dict[lang]).all()
    for key, value in translations:
        locals[str(key)] = value

    return locals


def get_feature_info(id, srid, translations):
    """The function gets the geometry of a parcel by it's ID and does an overlay
    with other administrative layers to get the basic parcelInfo and attribute
    information of the parcel : municipality, local names, and so on

    hint:
    for debbuging the query use str(query) in the console/browser window
    to visualize geom.wkt use session.scalar(geom.wkt)
    """
    try:
        SRS = srid
    except:
        SRS = 2056

    parcelInfo = {}
    parcelInfo['featureid'] = None
    Y = None
    X = None

    if id:
        parcelInfo['featureid'] = id
    # elif request.params.get('X') and request.params.get('Y') :
        # X = int(request.params.get('X'))
        # Y = int(request.params.get('Y'))
    else:
        raise Exception(translations[''])

    if parcelInfo['featureid'] is not None:
        queryresult = DBSession.query(Property).filter_by(id=parcelInfo['featureid']).first()
        # We should check unicity of the property id and raise an exception if there are multiple results
    elif (X > 0 and Y > 0):
        if Y > X:
            pointYX = WKTElement('POINT('+str(Y)+' '+str(X)+')', SRS)
        else:
            pointYX = WKTElement('POINT('+str(X)+' '+str(Y)+')', SRS)
        queryresult = DBSession.query(Property).filter(Property.geom.ST_Contains(pointYX)).first()
        parcelInfo['featureid'] = queryresult.id
    else:
        # to define
        return HTTPBadRequest(translations['HTTPBadRequestMsg'])

    parcelInfo['geom'] = queryresult.geom
    parcelInfo['area'] = int(queryresult.srfmai)
    parcelInfo['computed_area'] = int(round(DBSession.scalar(queryresult.geom.ST_Area()), 0))
    parcelInfo['area_ratio'] = round(queryresult.srfmai/DBSession.scalar(queryresult.geom.ST_Area()),4)

    if isinstance(LocalName, type) is False:
        queryresult1 = DBSession.query(LocalName).filter(LocalName.geom.ST_Intersects(parcelInfo['geom'])).first()
        parcelInfo['lieu_dit'] = queryresult1.nomloc  # Flurname

    queryresult2 = DBSession.query(Town).filter(Town.geom.ST_Buffer(1).ST_Contains(parcelInfo['geom'])).first()

    parcelInfo['nummai'] = queryresult.nummai  # Parcel number
    parcelInfo['type'] = queryresult.typimm  # Parcel type
    if 'egrid' in queryresult.__table__.columns.keys() and queryresult.egrid is not None:
        parcelInfo['egrid'] = queryresult.egrid
    else:
        parcelInfo['egrid'] = translations['noEGRIDtext']

    if parcelInfo['type'] is None:
        parcelInfo['type'] = translations['UndefinedPropertyType']

    if 'numcad' in queryresult2.__table__.columns.keys():
        parcelInfo['nomcad'] = queryresult2.cadnom

    parcelInfo['numcom'] = queryresult.numcom
    parcelInfo['nomcom'] = queryresult2.comnom
    parcelInfo['nufeco'] = queryresult2.nufeco
    parcelInfo['centerX'] = DBSession.scalar(functions.ST_X(queryresult.geom.ST_Centroid()))
    parcelInfo['centerY'] = DBSession.scalar(functions.ST_Y(queryresult.geom.ST_Centroid()))
    parcelInfo['BBOX'] = get_bbox_from_geometry(DBSession.scalar(functions.ST_AsText(queryresult.geom.ST_Envelope())))

    # the get_print_format function is not needed any longer as the paper size has been fixed to A4 by the cantons
    # but we keep the code because the decision will be revoked
    # parcelInfo['printFormat'] = get_print_format(parcelInfo['BBOX'])

    return parcelInfo


def get_bbox_from_geometry(geometry):
    """Returns the BBOX coordinates of an rectangle. Input : rectangle; output : bbox
       coordListStr : String with the list of the X,Y coordinates of the bounding box
       X,Y : coordinates in Swiss national projection
       bbox : Resulting dictionary with lower left (minX,minY) and upper right corner (maxX,maxY)
    """

    coordListStr = geometry.split("(")[2].split(")")[0].split(',')
    X = []
    Y = []
    for coordStr in coordListStr:
        X.append(float(coordStr.split(" ")[0]))
        Y.append(float(coordStr.split(" ")[1]))

    bbox = {'minX': min(X), 'minY': min(Y), 'maxX': max(X), 'maxY': max(Y)}

    return bbox


def get_print_format(bbox, fitRatio):
    """Detects the best paper format and scale in function of the general form and size of the parcel
    This function determines the optimum scale and paper format (if different paper
    formats are available) for the pdf print in dependency of the general form of
    the selected parcel.
    """

    printFormat = {}

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Enhancement : take care of a preselected paper format by the user
    # ===================
    formatChoice = 'A4'
    # if fixedpaperformat == True:
    #     paperFormats = {predefinedPaperFormat}
    # else:
    # Gets the list of all available formats and their parameters : name, orientation, height, width
    paperFormats = DBSession.query(PaperFormats).order_by(PaperFormats.scale.asc()).order_by(PaperFormats.orientation.desc()).all()

    fit = 'false'
    # fitRation defines the minimum spare space between the property limits and the map border. Here 10%
    # fitRatio = 0.9
    ratioW = 0
    ratioH = 0
    # Attention X and Y are standard carthesian and inverted in comparison to the Swiss Coordinate System
    deltaX = bbox['maxX'] - bbox['minX']
    deltaY = bbox['maxY'] - bbox['minY']
    resolution = 150  # 150dpi print resolution
    ratioInchMM = 25.4  # conversion inch to mm

    # Decides what parcel orientation
    if deltaX >= deltaY:
        # landscape
        bboxWidth = deltaX
        bboxHeight = deltaY
    else:
        # portrait
        bboxWidth = deltaY
        bboxHeight = deltaX

    # Get the appropriate paper format for the print
    for paperFormat in paperFormats:
        ratioW = bboxWidth*1000/paperFormat.width/paperFormat.scale
        ratioH = bboxHeight*1000/paperFormat.height/paperFormat.scale

        if ratioW <= fitRatio and ratioH <= fitRatio:
            printFormat.update(paperFormat.__dict__)
            printFormat['mapHeight'] = int(printFormat['height']/ratioInchMM*resolution)
            printFormat['mapWidth'] = int(printFormat['width']/ratioInchMM*resolution)
            fit = 'true'
            break

    return printFormat
