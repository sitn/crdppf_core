# -*- coding: UTF-8 -*-
from sqlalchemy import or_
from papyrus.geojsonencoder import dumps

from simplejson import loads as sloads
import csv
# import math

from crdppf.models import DBSession
from crdppfportal.table2model_match import table2model_match


def get_features_function(parcelGeom, params):

    # split the layer list string into proper python list
    csvReader = csv.reader([params['layerList']], skipinitialspace=True)

    # iterate over layer and make intersects queries
    itemList = []
    for item in csvReader:
        itemList.append(item)
    layerList = itemList[0]

#    test = 'empty'
#    # retrieve models from table2model
#    for layer in layerList:
#        model = table2model_match[layer]

    # spatial analysis
    featureList = []
    for layer in layerList:
        targetModel = table2model_match[layer]
        intersectResult = DBSession.query(targetModel).filter(or_(targetModel.geom.ST_Intersects(parcelGeom), targetModel.geom.ST_Within(parcelGeom))).all()
        if intersectResult:
            # create geojson output with custom attributes
            for feature in intersectResult:
                geometryType = DBSession.scalar(feature.geom.ST_GeometryType())
                geomType = ''
                intersectionMeasure = -9999
                intersectionMeasureTxt = ''
                if geometryType == 'ST_Polygon' or geometryType == 'ST_MultiPolygon':
                    intersectionMeasure = DBSession.scalar(feature.geom.ST_Intersection(parcelGeom).ST_Area())
                    if intersectionMeasure >= 1:
                        intersectionMeasureTxt = ' : ' + str(int(round(intersectionMeasure, 0))) + ' [m2]'
                        geomType = 'Polygone'
                        jsonFeature = sloads(dumps(feature))
                        jsonFeature['properties']['layerName'] = layer
                        jsonFeature['properties']['intersectionMeasure'] = intersectionMeasureTxt
                        jsonFeature['properties']['geomType'] = 'area'
                        featureList.append(jsonFeature)
                elif geometryType == 'ST_Line' or geometryType == 'ST_MultiLineString' or geometryType == 'ST_LineString':
                    intersectionMeasure = DBSession.scalar(feature.geom.ST_Intersection(parcelGeom).ST_Length())
                    if intersectionMeasure >= 1:
                        intersectionMeasureTxt = ' : ' + str(int(round(intersectionMeasure, 0))) + ' [m]'
                        geomType = 'Ligne'
                        jsonFeature = sloads(dumps(feature))
                        jsonFeature['properties']['layerName'] = layer
                        jsonFeature['properties']['intersectionMeasure'] = intersectionMeasureTxt
                        jsonFeature['properties']['geomType'] = 'line'
                        featureList.append(jsonFeature)
                elif geometryType == 'ST_Point' or geometryType == 'ST_MultiPoint':
                    featureMeasure = -9999
                    geomType = 'Point'
                    intersectionMeasureTxt = ' '    # ' : point'
                    jsonFeature = sloads(dumps(feature))
                    jsonFeature['properties']['layerName'] = layer
                    jsonFeature['properties']['intersectionMeasure'] = intersectionMeasureTxt
                    jsonFeature['properties']['geomType'] = 'point'
                    featureList.append(jsonFeature)
                else:
                    return('Error on geometry type:' + geometryType)

    return featureList
