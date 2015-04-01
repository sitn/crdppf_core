Ext.namespace('Crdppf');
OpenLayers.ImgPath = Crdppf.OLImgPath;  

// Constructor
Crdppf.FeaturePanel = function Map() {    
    this.init();
};

Crdppf.FeaturePanel.prototype = {
    /**
    * Object: Feature tree to display intersection results
    * Parameters:
    * none
    */
    featureTree: new Ext.tree.TreePanel({
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
    }),
    /**
    * Object: Root of the featureTree
    * Parameters:
    * none
    */
    root: new Ext.tree.TreeNode({
        text: 'Thèmes',
        draggable:false,
        id:'rootNode'
    }),
    /**
    * Method: disable the existing info controls
    * Parameters:
    * none
    */
    disableInfoControl: function disableInfoControl(){
        this.featureTree.collapse(false);
        Crdppf.Map.intersectLayer.removeAllFeatures();
        this.featureTree.setTitle(Crdppf.labels.restrictionPanelTitle);
        this.root.removeAll(true);
        Crdppf.Map.selectLayer.removeAllFeatures();
        var infoControl = Crdppf.Map.map.getControl('infoControl001');

        if(infoControl){
            infoControl.destroy();
        }
    },
    /**
    * Method: create the info control
    * Parameters:
    * none
    */
    setInfoControl: function setInfoControl(){

        // avoid duplicating infoControls
        this.disableInfoControl();

        // remove all features in featureTree rootNode
        this.root.removeAll(true);
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
                Crdppf.FeaturePanel.PropertySelection(e.features, Crdppf.labels);
            // else the selected feature is highlighted 
            } else {
                property= e.features[0];
                Crdppf.FeaturePanel.featureSelection(property);
            }
        });
        control.events.register("featureunselected", this, function(e) {
            //Crdppf.Map.selectLayer.removeFeatures([e.feature]);
            this.root.removeAll(true);
        });
        Crdppf.Map.map.addControl(control);
        control.activate();
    },
    /***
    * Method: On multiple property selection (DP case) the user is ask to select only one
    * Parameters:
    * features:
    * labels: 
    */
    PropertySelection: function(features, labels) {
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
                        Crdppf.FeaturePanel.featureSelection(property);
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
    },
    /***
    * Method: On multiple property selection (DP case) the user is ask to select only one
    * Parameters:
    * features:
    * labels: 
    */
    featureSelection: function(property) {

        this.featureTree.expand(true);
        Crdppf.Map.intersectLayer.removeAllFeatures();
        Crdppf.Map.selectLayer.addFeatures([property]);

        var parcelId = property.attributes.idemai;
        Crdppf.docfilters({'cadastrenb': parseInt(parcelId.split('_',1)[0])});
        if(Crdppf.LayerTreePanel.overlaysList.length === 0){
            var top =  new Ext.tree.TreeNode({
                text: Crdppf.labels.noActiveLayertxt,
                draggable: false,
                leaf: true,
                expanded: true
            });
            this.root.appendChild(top);
        }
        else { // send intersection request and process results
                var me = this;
                function handler(request, me) {
                    var geojson_format = new OpenLayers.Format.GeoJSON();
                    var jsonData = geojson_format.read(request.responseText);
                    Crdppf.FeaturePanel.featureTree.setTitle(Crdppf.labels.restrictionPanelTxt + parcelId);
                    var lList = [];
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
                                Crdppf.FeaturePanel.root.appendChild(layerChild);
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
                        Crdppf.FeaturePanel.root.appendChild(layerChild);
                    }
            }
            // define an request object to the interection route
            var featureMask = new Ext.LoadMask(this.featureTree.body, {msg: Crdppf.labels.restrictionLoadingMsg});
            featureMask.show();

            var request = OpenLayers.Request.GET({
                url: Crdppf.getFeatureUrl,
                params: {
                    id: parcelId,
                    layerList: Crdppf.LayerTreePanel.overlaysList
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
    },
    /***
    * Method: initialize the feature tree 
    */
    init: function () {
        this.featureTree.setRootNode(this.root);
    }
};
