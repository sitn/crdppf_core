def get_content(id):
    
    d = {
        "datasource": []
    }
    
    for map in maps:
        d["datasource"].push({
            "map": {
                "projection": "EPSG:4326",
                "dpi": 72,
                "rotation": 0,
                "bbox": [-130, 20, -60, 50],
                "longitudeFirst": true,
                "layers": [{
                    "type": "geojson",
                    "..."
                },{
                    "type": "WMS",
                    "layers": ["topp:states"],
                    "baseURL": "http://localhost:9876/e2egeoserver/wms",
                    "imageFormat": "image/png",
                    "version": "1.1.1",
                    "customParams": {
                        "TRANSPARENT": "true"
                    }
                },{
                    "type": "WMTS",
                    "..."
                
                }]
            },
            "legend_url": "http://...&style=toto.xml"
        })
        
    # Legends:
    """
    
    """
        
    return d