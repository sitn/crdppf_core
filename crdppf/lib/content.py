from copy import deepcopy

def get_content(idemai, request):

    map = {
        "projection": "EPSG:21781",
        "dpi": 72,
        "rotation": 0,
        "bbox": [555932, 201899, 	556079, 202001],
        "longitudeFirst": "true",
        "layers": [{
            "type": "geojson",
            "geoJson": request.route_url('get_property')+'?ids='+idemai,
            "style": {
                "version": "2",
                "strokeColor": "gray",
                "strokeLinecap": "round",
                "strokeOpacity": 0.6,
                "fill": "red"
            }
        #~ }, {
            #~ "type": "WMS",
            #~ "layers": ["topp:states"],
            #~ "baseURL": "http://localhost:9876/e2egeoserver/wms",
            #~ "imageFormat": "image/png",
            #~ "version": "1.1.1",
            #~ "customParams": {
                #~ "TRANSPARENT": "true"
            #~ }
        #~ }, {
            #~ "type": "WMTS",
            #~ #"..."

        }]
    }
    #~ base_map = deepcopy(map)
    #~ base_map["bbox"] = " "
    
    d = {
    #    "datasource": [],
        "map": map,
     #   "base_map": base_map,
    }

    #~ maps = []


    #~ for map__ in maps:
        #~ my_map = deepcopy(map)
        #~ my_map["layers"][1]["layers"] = 'toto'
        #~ d["datasource"].push({
            #~ "map": my_map,
            #~ "legend_url": "http://...&style=toto.xml"
        #~ })

    d= {
        "attributes": {"map": {
            "bbox": [555932, 201899, 556079, 202001],
            "dpi": 72,
            "layers": [{
                "type": "geojson",
                "geoJson":"http://localhost:6544/property/get?ids=13_5199"
            }],
            "longitudeFirst": True,
            "projection": "EPSG:21781",
            "scale": 1000
        }},
        "layout": "report"
    }

    return d
