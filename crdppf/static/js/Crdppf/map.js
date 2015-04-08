/*
 * @include OpenLayers/Projection.js
 * @include OpenLayers/Map.js
 * @requires OpenLayers/Request.js 
 * @requires OpenLayers/Layer/WMTS.js 
 * @requires OpenLayers/Layer/Image.js 
 * @requires OpenLayers/Control/LayerSwitcher.js
 * @requires OpenLayers/Control/OverviewMap.js
 * @requires OpenLayers/Control/PanZoomBar.js
 * @requires OpenLayers/Control/GetFeature.js
 * @requires OpenLayers/Control/ScaleLine.js
 * @requires OpenLayers/Control/Measure.js
 * @requires OpenLayers/Handler/Path.js
 * @requires OpenLayers/Handler/Polygon.js
 * @requires OpenLayers/Handler.js
 * @requires OpenLayers/Util.js 
 * @requires OpenLayers/Rule.js
 * @requires OpenLayers/Control/Navigation.js
 * @include OpenLayers/Layer/WMS.js
 * @include OpenLayers/Layer/Vector.js
 * @include OpenLayers/Format/GML.js
 * @include OpenLayers/Format/GeoJSON.js
 * @include OpenLayers/Renderer/Canvas.js
 * @include OpenLayers/Renderer/Elements.js
 * @include OpenLayers/Renderer/SVG.js
 * @include OpenLayers/Renderer/VML.js
 * @include OpenLayers/Protocol/WFS/v1_0_0.js
 * @include OpenLayers/Protocol/WFS.js
 */

Ext.namespace('Crdppf');
OpenLayers.ImgPath = Crdppf.OLImgPath;  

Crdppf.Map = function (){
    this.mapInit();
};

Crdppf.Map.prototype = {
    infoControl: null,
    createInfoControl: function(){
        OpenLayers.ProxyHost = Crdppf.ogcproxyUrl;
        // OL WFS protocol
        var protocol = new OpenLayers.Protocol.WFS({
            url: Crdppf.ogcproxyUrl,
            geometryName: this.geometryName,
            srsName: this.map.getProjection(),
            featureType: 'parcelles',
            formatOptions: {
                featureNS: 'http://mapserver.gis.umn.edu/mapserver',
                autoconfig: false
            }
        });

        // create infoControl with OL WFS protocol
       var control = new OpenLayers.Control.GetFeature({
            protocol: protocol,
            box: false,
            hover: false,
            single: false,
            maxFeatures: 4,
            clickTolerance: 15
        });

        control.events.register("beforefeaturesselected", this, function(e) {
            Crdppf.Map.selectLayer.removeAllFeatures();
        });

        control.events.register("beforefeatureselected", this, function(e) {
            Crdppf.Map.selectLayer.removeAllFeatures();
        });

        // define actions on feature selection
        control.events.register("featuresselected", this, function(e) {
            // if there is more than one feature, we present the user with a selection window
            if (e.features.length > 1) {
                Crdppf.FeaturePanel.PropertySelection(e.features, Crdppf.labels);
            // else the selected feature is highlighted 
            } else {
                property = e.features[0];
                Crdppf.FeaturePanel.featureSelection(property);
            }
        });
        control.events.register("featureunselected", this, function(e) {
            Crdppf.FeaturePanel.root.removeAll(true);
        });
        this.infoControl = control;
        this.map.addControl(this.infoControl);
        this.infoControl.activate();
    },
    /**
    * Object: OL layer to display feature query results
    * Parameters:
    * none
    */
    selectLayer: new OpenLayers.Layer.Vector(
        "Selection",
        {
            styleMap: new OpenLayers.Style({
                'strokeColor':'#00ff00',
                'fillOpacity': '0.5',
                'fillColor': '#00ff00',
                'strokeWidth':'3',
                'pointRadius': '20'
            }),
            fixedLayer: true, 
            displayInLayerSwitcher: false
    }),
    /**
    * Object: OL layer to display intersection results
    * Parameters:
    * none
    */
    intersectLayer: new OpenLayers.Layer.Vector(
        "Intersection result",
        {
            styleMap: new OpenLayers.Style({
                'strokeColor':'#ff0000',
                'fillOpacity': '0.5',
                'fillColor': '#ff0000',
                'strokeWidth':'2',
                'pointRadius': '20'
            }),
            fixedLayer: true,
            displayInLayerSwitcher: false
        }
    ),
    /**
    * Object: map base layer
    * Parameters:
    * none
    */ 
    baseLayer: new OpenLayers.Layer.WMTS({
        url: Crdppf.mapproxyUrl,
        layer: Crdppf.defaultTiles.wmtsname,
        matrixSet: Crdppf.mapMatrixSet,
        format: Crdppf.defaultTiles.tile_format,
        formatSuffixMap: {'image/png':'png'},
        isBaseLayer: true,
        style: 'default',
        fixedLayer: true,
        requestEncoding: 'REST'
    }),
    /**
    * Object: OpenLayers map object
    * Parameters:
    * none
    */ 
    map: new OpenLayers.Map({
        projection: new OpenLayers.Projection(Crdppf.mapSRS),
        resolutions: Crdppf.mapResolutions,
        units: 'm',
        theme: null,
        maxExtent: new OpenLayers.Bounds(Crdppf.mapMaxExtent),
        restrictedExtent: new OpenLayers.Bounds(Crdppf.mapExtent),
        controls: [
            new OpenLayers.Control.PanZoomBar({
                slideFactor: 300,
                zoomWorldIcon: true,
                panIcons: false
            }),
            new OpenLayers.Control.Navigation(),
            new OpenLayers.Control.ScaleLine({
                bottomOutUnits:'',
                bottomInUnits: '',
                maxWidth: 200
            }),
            new OpenLayers.Control.OverviewMap({
                layers: [
                    new OpenLayers.Layer.Image(
                        "overview",
                        Crdppf.staticImagesDir + Crdppf.keymap,
                        new OpenLayers.Bounds(Crdppf.mapOverviewExtent),
                        new OpenLayers.Size(Crdppf.mapOverviewSizeW, Crdppf.mapOverviewSizeH)
                    )
                ],
                size: new OpenLayers.Size(Crdppf.mapOverviewSizeW, Crdppf.mapOverviewSizeH),
                maximized: true,
                isSuitableOverview: function() {
                    return true;
                },
                mapOptions: {
                    projection: new OpenLayers.Projection(Crdppf.mapSRS),
                    displayProjection: new OpenLayers.Projection(Crdppf.mapSRS),
                    units: "m",
                    theme: null
                }
            })
        ]
    }),
    // The map initialization function
    mapInit : function(){

        // scope trick
        var me = this;

        // Show coordinates on mouse move
        this.map.events.register("mousemove", me.map, function(e) {
            var pixel = new OpenLayers.Pixel(e.xy.x,e.xy.y);
            var lonlat = this.getLonLatFromPixel(pixel);
            OpenLayers.Util.getElement('mousepos').innerHTML = '<b>' + Crdppf.labels.olCoordinates + ' (ch1903) - Y : ' + Math.round(lonlat.lon) + ' m / X : ' + Math.round(lonlat.lat) + ' m</b>';
        });

        // Set layers'id
        this.intersectLayer.id = 'intersectLayer';    
        this.selectLayer.id = 'selectionLayer';  
        this.baseLayer.id = 'baseLayer';

        // layers to map
        this.map.addLayers([this.intersectLayer, this.selectLayer, this.baseLayer]);

        // Zoom to max extent
        this.map.zoomToMaxExtent();

        this.createInfoControl();
    },
    /**
    * Method: setOverlays
    * Set the layers to be added to the map depending on the crdppf thematic selected. All layer a group in one single WMS
    *
    * Parameters:
    * none
    */ 
    setOverlays: function() {
        // Deactivate infoControl
        this.infoControl.deactivate();

        var layerName = 'Themes';
        var theLayer = this.map.getLayer('overlayLayer');
        if(theLayer){
            this.map.removeLayer(theLayer);
        }
        // add new overlays
        if(Crdppf.LayerTreePanel.overlaysList.length > 0){
            var loadMask = new Ext.LoadMask(Ext.getCmp('themePanel').body, {msg: Crdppf.labels.layerLoadingMaskMsg});
            var overlays = new OpenLayers.Layer.WMS(
                layerName, 
                Crdppf.wmsUrl,
                {
                    layers: Crdppf.LayerTreePanel.overlaysList,
                    format: 'image/png',
                    singleTile: true,
                    transparent: 'true'
                },{
                    singleTile: true,
                    isBaseLayer: false
                }
            );

            // Listen to layers events and show loading mask whenever necessary
            overlays.events.register("loadstart", overlays, function() {
                if (Crdppf.LayerTreePanel.overlaysList.length > 0) {
                    loadMask.show();
                }
            });        
            overlays.events.register("loadend", overlays, function() {
                loadMask.hide();
            });
  
            overlays.events.register("tileloaded", overlays, function() {
                loadMask.hide();
            });
            overlays.id = 'overlayLayer';

            this.map.addLayer(overlays);
            this.map.raiseLayer(this.selectLayer, this.map.layers.length);
        }
    }
};
