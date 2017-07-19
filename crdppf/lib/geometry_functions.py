# -*- coding: UTF-8 -*-

from crdppf.models import DBSession
from crdppf.models import Property, PaperFormats

from sqlalchemy.sql import func

def get_feature_center(id):
    """ Extract a feature centroid regarding its id attribute
    """

    geom = DBSession.query(Property.geom).filter(Property.id==id).all()

    if len(geom) > 1:
        return False
    else:
        geom = geom[0][0]

    return [
        DBSession.scalar(geom.ST_Centroid().ST_X()),
        DBSession.scalar(geom.ST_Centroid().ST_Y())
    ]

def get_feature_bbox(id):
    """ Extract a feature centroid regarding its id attribute
    """

    box = DBSession.query(func.ST_extent(Property.geom)). \
        filter(Property.id==id).all()

    if len(box) > 1:
        return False
    else:
        box = box[0][0]
    
    box = box.split('(')[1].split(')')[0].replace(',', ' ').split(' ')

    return {
        'minX': float(box[0]),
        'minY': float(box[1]),
        'maxX': float(box[2]),
        'maxY': float(box[3]),
    }

def get_print_format(bbox, fitRatio):
    """ Detects the best paper format and scale in function of the general form
    and size of the parcel.
    This function determines the optimum scale and paper format (if different paper 
    formats are available) for the pdf print in dependency of the general form of 
    the selected parcel.
    """

    printFormat = {}

    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Enhancement : take care of a preselected paper format by the user
    # ===================
    formatChoice = 'A4'
    # if fixedpaperformat == True:
    #     paperFormats = {predefinedPaperFormat}
    # else:
    # Gets the list of all available formats and their parameters : name,
    # orientation, height and width
    paperFormats = DBSession.query(PaperFormats). \
        order_by(PaperFormats.scale.asc()).order_by(PaperFormats.orientation.desc()). \
        all()

    fit = 'false'
    # fitRation defines the minimum spare space between the property limits
    #and the map border. Here 10%
    # fitRatio = 0.9
    ratioW = 0
    ratioH = 0
    # Attention X and Y are standard carthesian and inverted in comparison to
    # the Swiss Coordinate System 
    deltaX = bbox['maxX'] - bbox['minX']
    deltaY = bbox['maxY'] - bbox['minY']
    resolution = 150 # 150dpi print resolution
    ratioInchMM = 25.4 # conversion inch to mm

    # Decides what parcel orientation 
    if deltaX >= deltaY :
        # landscape
        bboxWidth = deltaX
        bboxHeight = deltaY
    else :
        # portrait
        bboxWidth = deltaY
        bboxHeight = deltaX

    # Get the appropriate paper format for the print
    for paperFormat in paperFormats :
        ratioW = bboxWidth*1000/paperFormat.width/paperFormat.scale
        ratioH = bboxHeight*1000/paperFormat.height/paperFormat.scale

        if ratioW <= fitRatio and ratioH <= fitRatio :
            printFormat.update(paperFormat.__dict__)

            printFormat.pop("_sa_instance_state", None)

            printFormat['mapHeight'] = int(
                printFormat['height']/ratioInchMM*resolution
            )

            printFormat['mapWidth'] = int(
                printFormat['width']/ratioInchMM*resolution
            )

            fit = 'true'
            break

    return printFormat
