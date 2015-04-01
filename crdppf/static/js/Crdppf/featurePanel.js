Ext.namespace('Crdppf');
OpenLayers.ImgPath = Crdppf.OLImgPath;  

// Constructor
Crdppf.FeaturePanel = function Map() {
    this.title = 'Crdppf feature panel';
    this.description = 'Display info on feature query';       
    this.setInfoControl = setInfoControl;
    this.disableInfoControl = disableInfoControl;
    this.root = root;
    this.featureTree = featureTree;
};


// featureTree displayed in infoPanel as a global view 
var featureTree = new Ext.tree.TreePanel({
    title: Crdppf.labels.restrictionPanelTitle,
    cls: 'featureTreeCls',
    collapsed: false,
    useArrows:false,
    collapside: false,
    animate:true,
    lines: false,
    enableDD:false,
    rootVisible: false,
    frame: false,
    id: 'featureTree',
    height:300,
    autoScroll: true
});

var root = new Ext.tree.TreeNode({
    text: 'Thèmes',
    draggable:false,
    id:'rootNode'
});

featureTree.setRootNode(root);

// var layerStore = new GeoExt.data.LayerStore({
    // map: Crdppf.Map.map
// });

// Disable the existing infoControls
var disableInfoControl = function disableInfoControl(){
    featureTree.collapse(false);
    Crdppf.Map.intersectLayer.removeAllFeatures();
    featureTree.setTitle(Crdppf.labels.restrictionPanelTitle);
    root.removeAll(true);
    var selectionLayer = Crdppf.Map.map.getLayer('selectionLayer');
    Crdppf.Map.selectLayer.removeAllFeatures();
    var infoControl = Crdppf.Map.map.getControl('infoControl001');

    if(infoControl){
        infoControl.destroy();
    }
};

// Create the infocontrols supporting the getFeatureInfo functionnalities
var setInfoControl = function setInfoControl(){

    // avoid duplicating infoControls
    this.disableInfoControl();

    // remove all features in featureTree rootNode
    root.removeAll(true);
    OpenLayers.ProxyHost= Crdppf.ogcproxyUrl;
    // create OL WFS protocol
    var protocol = new OpenLayers.Protocol.WFS({
        url: Crdppf.ogcproxyUrl,
        geometryName: this.geometryName,
        srsName: Crdppf.Map.map.getProjection(),
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
        Crdppf.Map.selectLayer.removeFeatures([e.feature]);
        root.removeAll(true);
    });
    Crdppf.Map.map.addControl(control);
    control.activate();
};

    
// On multiple property selection (DP case) the user is ask to select only one
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
    Crdppf.Map.intersectLayer.removeAllFeatures();
    Crdppf.Map.selectLayer.addFeatures([property]);

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
                                            Crdppf.Map.intersectLayer.removeAllFeatures();
                                            feature = node.attributes.attributes;
                                            Crdppf.Map.intersectLayer.addFeatures(feature);
                                            Crdppf.Map.map.zoomToExtent(feature.geometry.bounds);
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