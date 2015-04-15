Ext.namespace('Crdppf');
OpenLayers.ImgPath = Crdppf.OLImgPath;  

// Constructor
Crdppf.FeaturePanel = function Map() {    
    this.init();
};

Crdppf.FeaturePanel.prototype = {
    /**
    * Property: currently selected property
    **/
    currentProperty: null,
    /**
    * Object: Feature tree to display intersection results
    * Parameters:
    * none
    */
    featureTree: new Ext.tree.TreePanel ({
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
    root: new Ext.tree.TreeNode ({
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
        this.root.removeAll(true);
        this.featureTree.setTitle(Crdppf.labels.restrictionPanelTitle);
        Crdppf.Map.selectLayer.removeAllFeatures();
        Crdppf.currentProperty = null;
        Crdppf.Map.intersectLayer.removeAllFeatures();
        Crdppf.Map.infoControl.deactivate();
    },
    /**
    * Method: create the info control
    * Parameters:
    * none
    */
    setInfoControl: function setInfoControl(){
        Ext.getCmp('infoButton').toggle(true);
        Crdppf.Map.infoControl.activate();
        this.root.removeAll(true);
    },
    /***
    * Method: On multiple property selection (DP case) the user is ask to select only one
    * Parameters:
    * features:
    * labels: 
    */
    PropertySelection: function(features, labels) {
        
        var propertySelectionWindow;
        
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

            var comboFeatureSelect = new Ext.form.ComboBox({
                store: new Ext.data.ArrayStore({
                    fields: ['index','displaytxt','idemai','idemai'],
                    data: properties 
                }),
                displayField: 'displaytxt',
                valueField: 'index',
                typeAhead: true,
                mode: 'local',
                triggerAction: 'all',
                emptyText: labels.choosePropertyMsg,
                selectOnFocus: true,
                listeners: {
                    select: function(combo, record, index) {
                        var property = features[index];
                        Crdppf.FeaturePanel.featureSelection(property);
                        Crdppf.currentProperty = property;
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
                id: 'propertySelectionWindow',
                closeAction: 'hide',
                items: [comboFeatureSelect],
                listeners: {
                    hide: function() {
                        this.hide();
                    }
                }
            });

            propertySelectionWindow.show();
        } else {
            return 0;
        }
    },
    /***
    * Method: get restrictions and insert them into the restriction treePanel
    */
    insertRestrictions: function (request, me) {
        var geojson_format = new OpenLayers.Format.GeoJSON();
        var jsonData = geojson_format.read(request.responseText);
        Crdppf.FeaturePanel.featureTree.setTitle(Crdppf.labels.restrictionPanelTxt + Crdppf.currentProperty.attributes.idemai);
        var lList = [];
        // iterate over the restrictions found
        Crdppf.FeaturePanel.root.removeAll(true);
        for (var i = 0; i < jsonData.length; i++) {
            lName = jsonData[i].attributes.layerName;
            // create node for layer if not already created
            if (!Crdppf.contains(lName,lList)){
                var fullName = '';
                var ll = Crdppf.layerList.themes;
                for (var l=0; l < ll.length; l++){
                    for (var key in ll[l].layers){
                        if (lName == key){
                            fullName = Crdppf.labels[key]; 
                        }
                    }
                }
                // create layer node (level 1, root is level 0 in the hierarchy)
                var layerChild = new Ext.tree.TreeNode({
                    text: fullName,
                    draggable: false,
                    id: Crdppf.uuid(),
                    leaf: false,
                    expanded: true
                });

                // iterate over all features: create a node for each restriction and group them by their owning layer
                for (var j=0; j < jsonData.length; j++) {
                    if (jsonData[j].attributes.layerName == lName){
                        Crdppf.docfilters({'objectids': [jsonData[i].fid]});
                        featureClass = jsonData[j].attributes.featureClass;
                        html = '';
                        // Attribute keys are: statutjuridique, teneur, layerName, datepublication
                        for (var value in jsonData[j].attributes){
                            if (value !== 'geomType' && value !=='theme' && value !=='codegenre' && value !=='intersectionMeasure'){
                                if (value === 'layerName'){
                                    // Replace the layername as defined in the database by it's display name
                                    html += '<p class=featureAttributeStyle><b>' + Crdppf.labels[value] + ' : </b>' + Crdppf.labels[jsonData[j].attributes[value]] +'</p>';
                                } else {
                                    html += '<p class=featureAttributeStyle><b>' + Crdppf.labels[value] + ' : </b>' + jsonData[j].attributes[value] +'</p>';
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
            this.root.appendChild(layerChild);
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
        
        // Update legal documents
        Crdppf.docfilters({'cadastrenb': parseInt(parcelId.split('_',1)[0])});
        
        // If no result, display no results message
        if (Crdppf.LayerTreePanel.overlaysList.length === 0) {
            var top =  new Ext.tree.TreeNode({
                text: Crdppf.labels.noActiveLayertxt,
                draggable: false,
                leaf: true,
                expanded: true
            });
            this.root.appendChild(top);
            return;
        }
        var me = this;
        
        // define an request object to the interection route
        var featureMask = new Ext.LoadMask(this.featureTree.body, {msg: Crdppf.labels.restrictionLoadingMsg});
        featureMask.show();

        OpenLayers.Request.GET({
            url: Crdppf.getFeatureUrl,
            params: {
                id: parcelId,
                layerList: Crdppf.LayerTreePanel.overlaysList
            },
            callback: this.insertRestrictions,
            success: function(){
                featureMask.hide();
            },
            failure: function(){
                featureMask.hide();
            },
            proxy: null
        });
    },
    /***
    * Method: initialize the feature tree 
    */
    init: function () {
        this.featureTree.setRootNode(this.root);
    }
};
