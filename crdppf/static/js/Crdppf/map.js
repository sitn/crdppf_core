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

// Constructor
Crdppf.Map = function Map(mapOptions, labels) {
    this.title = 'Crdppf OpenLayers custom map object';
    this.description = 'Manages all cartographic parameters and actions';       
    this.map = makeMap(mapOptions, labels);
    this.setOverlays = setOverlays;
    this.setInfoControl = setInfoControl;
    this.disableInfoControl = disableInfoControl;
};

// Create the infocontrols supporting the getFeatureInfo functionnalities
var setInfoControl = function setInfoControl(){
    
    // avoid duplicating infoControls
    MapO.disableInfoControl();
    
    // remove all features in featureTree rootNode
    root.removeAll(true);

    OpenLayers.ProxyHost= Crdppf.ogcproxyUrl;
    // create OL WFS protocol
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

    // create infoControl with our WFS protocol
   var control = new OpenLayers.Control.GetFeature({
        protocol: protocol,
        id: 'infoControl001',
        box: false,
        hover: false,
        single: false,
        maxFeatures: 4,
        clickTolerance: 15
    });
        
    Crdppf.PropertySelection = function(features, labels) {
        
        var propertySelectionWindow;
        
        if (store) {
            store.removeAll();
        }
        
        if (features.length > 1) {
            var properties = [];
            for (var i = 0; i < features.length; i++){
                properties[i] = [
                i,
                features[i].data.typimm+': '+features[i].data.nummai+' '+features[i].data.cadastre,
                features[i].data.idemai,
                features[i].data.source
                ];
            }

            var store = new Ext.data.ArrayStore({
                fields: ['index','displaytxt','idemai','idemai'],
                data: properties 
            });
            
            var combo = new Ext.form.ComboBox({
                store: store,
                displayField: 'displaytxt',
                valueField: 'index',
                typeAhead: true,
                mode: 'local',
                triggerAction: 'all',
                emptyText: labels.choosePropertyMsg,
                selectOnFocus: true,
                listeners: {
                    select: function(combo, record, index) {
                        // the index of the selected feature is returned and used to highlight the geom
                        property = features[index];
                        Crdppf.featureSelection(property);
                        propertySelectionWindow.hide();
                    }
                }
            });

            if (propertySelectionWindow) {
                propertySelectionWindow.destroy();
            }
                
            propertySelectionWindow = new Ext.Window({
                title: Crdppf.labels.choosePropertyLabel,
                width: 300,
                autoHeight: true,
                layout: 'fit',
                closeAction: 'hide',
                items: [combo],
                listeners: {
                    hide: function() {
                        this.hide();
                        store.removeAll();
                    }
                }
            });
            
            propertySelectionWindow.show();
        } else {
            return 0;
        }
    };

    Crdppf.featureSelection = function(property) {

        featureTree.expand(true);
        intersect.removeAllFeatures();
        select.addFeatures([property]);
        
        var parcelId = property.attributes.idemai;
        Crdppf.docfilters({'cadastrenb': parseInt(parcelId.split('_',1)[0])});
        if(overlaysList.length === 0){
            var top =  new Ext.tree.TreeNode({
                text: Crdppf.labels.noActiveLayertxt,
                draggable: false,
                leaf: true,
                expanded: true
            });
            root.appendChild(top);
        }
        else { // send intersection request and process results
                function handler(request) {
                    var geojson_format = new OpenLayers.Format.GeoJSON();
                    // jsonData will contain the object with
                    // fid = objectid in the database = restrictionid
                    // attributes/data = [codegenre, datepublication, geomType, intersectionMeasure, layername, statutjuridique, teneur, theme]
                    // geometry = OpenLayers geometry type
                    var jsonData = geojson_format.read(request.responseText);
                    featureTree.setTitle(Crdppf.labels.restrictionPanelTxt + parcelId);
                    lList = [];
                    // iterate over the restriction found
                    for (var i=0; i<jsonData.length;i++) {
                        lName = jsonData[i].attributes.layerName;
                        // create node for layer if not already created
                        if(!Crdppf.contains(lName,lList)){
                            var fullName = '';
                            var ll = Crdppf.layerList.themes;
                            for (var l=0;l<ll.length;l++){
                                for (var key in ll[l].layers){
                                    if(lName==key){
                                        fullName = Crdppf.labels[key]; 
                                    }
                                }
                            }
                            // create layer node (level 1, root is level 0 in the hierarchy)
                            var layerChild =  new Ext.tree.TreeNode({
                                text: fullName,
                                draggable: false,
                                id: Crdppf.uuid(),
                                leaf: false,
                                expanded: true
                            });
                            
                            // iterate over all features: create a node for each restriction and group them by their owning layer
                            for (var j=0; j<jsonData.length; j++) {
                                if (jsonData[j].attributes.layerName == lName){
                                    Crdppf.docfilters({'objectids': [jsonData[i].fid]});
                                    featureClass = jsonData[j].attributes.featureClass;
                                    html = '';
                                    // Attribute keys are: statutjuridique, teneur, layerName, datepublication
                                    for (var value in jsonData[j].attributes){
                                        if (value !== 'geomType' && value !=='theme' && value!=='codegenre' && value!=='intersectionMeasure'){
                                            if (value === 'layerName'){
                                                // Replace the layername as defined in the database by it's display name
                                                html += '<p class=featureAttributeStyle><b>' + Crdppf.labels[value] + ' : </b>' + Crdppf.labels[jsonData[j].attributes[value]] +'</p>' ;
                                            } else {
                                                html += '<p class=featureAttributeStyle><b>' + Crdppf.labels[value] + ' : </b>' + jsonData[j].attributes[value] +'</p>' ;
                                            }
                                        }
                                    }
                                    html += '';
                                    // create 1 node for each restriction (level 2)
                                    var sameLayerNode = new Ext.tree.TreeNode({
                                        singleClickExpand: true,
                                        attributes: jsonData[j],
                                        text: Crdppf.labels.restrictionFoundTxt + (j+1) + ' : ' + String(jsonData[j].data.intersectionMeasure),
                                        draggable: false,
                                        leaf: false,
                                        expanded: false,
                                        id: Crdppf.uuid(),
                                        listeners: {
                                            'click': function(node,e) {
                                                intersect.removeAllFeatures();
                                                feature = node.attributes.attributes;
                                                intersect.addFeatures(feature);
                                                MapO.map.zoomToExtent(feature.geometry.bounds);
                                            }
                                        }
                                    });
                                    // create node containing the feature attributes (level 3)
                                    var contentNode = new Ext.tree.TreeNode({
                                        cls: 'contentNodeCls',
                                        text: html,
                                        draggable: false,
                                        leaf: false,
                                        expanded: false,
                                        id: Crdppf.uuid()
                                    });
                                    sameLayerNode.appendChild(contentNode);
                                    layerChild.appendChild(sameLayerNode);
                                }
                                root.appendChild(layerChild);
                            }
                            lList.push(lName);
                        }
                    }
                    if (jsonData.length === 0){
                        // create layer node (level 1, root is level 0 in the hierarchy)
                        var layerChild =  new Ext.tree.TreeNode({
                            text: Crdppf.labels.noRestrictionFoundTxt,
                            draggable: false,
                            id: Crdppf.uuid(),
                            leaf: false,
                            expanded: true
                        });
                        root.appendChild(layerChild);
                    }
            }
            // define an request object to the interection route
            
            var featureMask = new Ext.LoadMask(featureTree.body, {msg: Crdppf.labels.restrictionLoadingMsg});
            featureMask.show();
            
            var request = OpenLayers.Request.GET({
                url: Crdppf.getFeatureUrl,
                params: {
                    id: parcelId,
                    layerList: overlaysList
                },
                callback: handler,
                success: function(){
                    featureMask.hide();
                },
                failure: function(){
                    featureMask.hide();
                },
                proxy: null
            });
        }   
        
        };
    // define actions on feature selection
    control.events.register("featuresselected", this, function(e) {
        // if there is more than one feature, we present the user with a selection window
        if (e.features.length > 1) {
            Crdppf.PropertySelection(e.features, Crdppf.labels);
        // else the selected feature ist highlighted 
        } else {
            property= e.features[0];
            Crdppf.featureSelection(property);
        }
    });
    control.events.register("featureunselected", this, function(e) {
        select.removeFeatures([e.feature]);
        root.removeAll(true);
    });
    this.map.addControl(control);
    control.activate();
};

// Create OL map object, add base layer & zoom to max extent
function makeMap(mapOptions, labels){

    // base layer: topographic layer
    var layer = new OpenLayers.Layer.WMTS({
        url: Crdppf.mapproxyUrl,
        layer: Crdppf.defaultTiles.wmtsname,
        matrixSet: Crdppf.mapMatrixSet,
        format: Crdppf.defaultTiles.tile_format,
        formatSuffixMap: {'image/png':'png'},
        isBaseLayer: true,
        style: 'default',
        fixedLayer: true,
        requestEncoding: 'REST'
    }); 
    
    layer.id = 'baseLayer';  
    
    var selectStyle = new OpenLayers.Style({
        'strokeColor':'#00ff00',
        'fillOpacity': '0.5',
        'fillColor': '#00ff00',
        'strokeWidth':'3',
        'pointRadius': '20'
    });    
    
    // selection layer: display selected features
    select = new OpenLayers.Layer.Vector(
        "Selection",
        {
            styleMap: selectStyle,
            fixedLayer: true, 
            displayInLayerSwitcher: false
    });
    
    select.id = 'selectionLayer';
    
    var intersectStyle = new OpenLayers.Style({
            'strokeColor':'#ff0000',
            'fillOpacity': '0.5',
            'fillColor': '#ff0000',
            'strokeWidth':'2',
            'pointRadius': '20'
        });
        
    intersect = new OpenLayers.Layer.Vector(
            "intersection result",
            {
                styleMap: intersectStyle,
                fixedLayer: true, 
                displayInLayerSwitcher: false
            }
        );
    intersect.id='intersectLayer';
    
    var scalebar = new OpenLayers.Control.ScaleLine({
        bottomOutUnits:'',
        bottomInUnits: '',
        maxWidth: 200
    });
  
    // THE OL map object
    var map = new OpenLayers.Map({
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
            scalebar            
        ]
    });   

        
    // Event registering & Control setting on the Map Object
    map.events.register("mousemove", map, function(e) {
                var pixel = new OpenLayers.Pixel(e.xy.x,e.xy.y);
                var lonlat = map.getLonLatFromPixel(pixel);
                OpenLayers.Util.getElement(mapOptions.divMousePosition).innerHTML = '<b>' + labels.olCoordinates + ' (ch1903) - Y : ' + Math.round(lonlat.lon) + ' m / X : ' + Math.round(lonlat.lat) + ' m</b>';
    });
    
    // add base layers & selection layers
    map.addLayers([intersect,select, layer]);
  
    // create an overview map control and customize it
    var overviewMap = new OpenLayers.Control.OverviewMap({
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
        });
    map.addControl(overviewMap);
    map.zoomToMaxExtent(); 
        
    return map;
}

// Disable the existing infoControls
var disableInfoControl = function disableInfoControl(){
    featureTree.collapse(false);
    intersect.removeAllFeatures();
    featureTree.setTitle(Crdppf.labels.restrictionPanelTitle);
    root.removeAll(true);
    var selectionLayer = this.map.getLayer('selectionLayer');
    selectionLayer.removeAllFeatures();
    infoControl = this.map.getControl('infoControl001');
    
    if(infoControl){
        infoControl.destroy();
    }
};

/**
* Method: setOverlays
* Set the layers to be added to the map depending on the crdppf thematic selected. All layer a group in one single WMS
*
* Parameters:
* none
*/ 
var setOverlays = function() {

    // remove existing infoControl
    infoControl = this.map.getControl('infoControl001');
    if(infoControl){
        infoControl.destroy();
    }
    // empty selection layer
    var selectionLayer = this.map.getLayer('selectionLayer');
    selectionLayer.removeAllFeatures();
    
    layerName = 'Themes';
    theLayer = this.map.getLayer('overlayLayer');
    if(theLayer){
        this.map.removeLayer(theLayer);
    }
    // add new overlays
    if(overlaysList.length > 0){
        var loadMask = new Ext.LoadMask(themeSelector.body, {msg: Crdppf.labels.layerLoadingMaskMsg});
        var overlays = new OpenLayers.Layer.WMS(
            layerName, 
            Crdppf.wmsUrl,
            {
                layers: overlaysList,
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
            loadMask.show();
        });        
        overlays.events.register("loadend", overlays, function() {
            loadMask.hide();
        });        
        overlays.events.register("tileloaded", overlays, function() {
            loadMask.show();
        });
        overlays.id = 'overlayLayer';
        this.map.addLayer(overlays);
        this.map.raiseLayer(this.map.getLayersBy('id', 'selectionLayer')[0], this.map.layers.length);

    }
    
};
