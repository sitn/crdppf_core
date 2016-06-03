# -*- coding: UTF-8 -*-

from xml.dom.minidom import parseString

from dogpile.cache.region import make_region
cache_region = make_region()
cache_region.configure("dogpile.cache.memory")

import httplib2

import logging

log = logging.getLogger(__name__)

@cache_region.cache_on_arguments()
def parse_wmts_getcapabilites(url):
    """ This cached function makes a HTTP request to retrieve the
        getcapabilities of a WMTS service
    """

    http = httplib2.Http()

    try:
        resp, content = http.request(url)
    except Exception as e:
        log.error(
            "Error '%s' while getting the URL:\n%s" %
            (sys.exc_info()[0], url)
        )

    dom = parseString(content)

    return dom

@cache_region.cache_on_arguments()
def wmts_layer(url, layer):
    """ Creates a dict compatible (through a json dump) as expected by
        MapFish print for a WMTS layer
    """

    dom = parse_wmts_getcapabilites(url)

    matrices = wmts_matrices(dom)

    encoding = dom.getElementsByTagName("ows:Value")
    encoding = encoding[0].firstChild.nodeValue

    operations = dom.getElementsByTagName("ows:Operation")

    version = dom.getElementsByTagName("Capabilities")[0]
    version = version.attributes['version'].nodeValue

    for operation in operations:
        if operation.attributes['name'].nodeValue == 'GetTile':
            get = operation.getElementsByTagName('ows:Get')
            baseUrl = get[0].attributes['xlink:href'].nodeValue
            requestEncoding = operation.getElementsByTagName('ows:Value')
            requestEncoding = requestEncoding[0].firstChild.nodeValue

    layers = dom.getElementsByTagName("Layer")

    dimensionParams = {}
    dimensions = []

    for layer_ in layers:
        if layer_.getElementsByTagName("ows:Identifier")[0].firstChild.nodeValue == layer:
            style = layer_.getElementsByTagName("Style")
            style = style[0].getElementsByTagName("ows:Identifier")[0].firstChild.nodeValue
            format = layer_.getElementsByTagName("Format")[0].firstChild.nodeValue

            format = format.split('/')

            # TODO, see https://github.com/mapfish/mapfish-print/issues/240
            if len(format) > 0:
                format = format[1]
            else:
                format = format[0]

            tilematrixset = layer_.getElementsByTagName("TileMatrixSet")[0].firstChild.nodeValue
            dimensions_ = layer_.getElementsByTagName("Dimension")
            if len(dimensions_) > 0:
                for dimension_ in dimensions_:                    
                    identifier = dimension_.getElementsByTagName("ows:Identifier")[0].firstChild.nodeValue
                    value = dimension_.getElementsByTagName("Value")[0].firstChild.nodeValue
                    dimensions.append(
                        identifier
                    )
                    dimensionParams[identifier] = value

    capabilities = {
        'baseURL': baseUrl,
        'requestEncoding': requestEncoding,
        'layer': layer,
        'type': 'wmts',
        'version': version,
        'matrices': matrices,
        'style': style,
        'imageFormat': format,
        'matrixSet': tilematrixset,
        'dimensionParams': dimensionParams,
        'dimensions': dimensions,
    }

    return capabilities


@cache_region.cache_on_arguments()
def wmts_matrices(dom):
    """ Creates a dict from the matrices information contained in the WMTS
        getCapabilities result
    """

    tile_matrices = dom.getElementsByTagName("TileMatrix")

    matrices = []

    for tile_matrice in tile_matrices:
        identifier = tile_matrice.getElementsByTagName('ows:Identifier')
        identifier = identifier[0].firstChild.nodeValue
        matrixWidth = tile_matrice.getElementsByTagName('MatrixWidth')
        matrixWidth = matrixWidth[0].firstChild.nodeValue
        matrixHeight = tile_matrice.getElementsByTagName('MatrixHeight')
        matrixHeight = matrixHeight[0].firstChild.nodeValue
        ScaleDenominator = tile_matrice.getElementsByTagName('ScaleDenominator')
        ScaleDenominator = ScaleDenominator[0].firstChild.nodeValue
        tileWidth = tile_matrice.getElementsByTagName('TileWidth')
        tileWidth = tileWidth[0].firstChild.nodeValue
        tileHeight = tile_matrice.getElementsByTagName('TileHeight')
        tileHeight = tileHeight[0].firstChild.nodeValue
        TopLeftCorner = tile_matrice.getElementsByTagName('TopLeftCorner')
        TopLeftCorner = TopLeftCorner[0].firstChild.nodeValue.split(' ')

        matrices.append({
            'identifier': identifier,
            'matrixSize': [int(matrixWidth), int(matrixHeight)],
            'scaleDenominator': float(ScaleDenominator),
            'tileSize': [int(tileWidth), int(tileHeight)],
            'topLeftCorner': [float(TopLeftCorner[0]), float(TopLeftCorner[1])],
        })

    return matrices
