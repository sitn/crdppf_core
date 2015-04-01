Ext.namespace('Crdppf');

Crdppf.ThemeSelector = function (labels, layerList, layerTree) {
    this.init(labels, layerList, layerTree);
};

Crdppf.ThemeSelector.prototype = {
    /***
    * The theme selector panel
    ***/
    themePanel: null,
    /***
    * The theme selector initialization
    ***/
    init: function(labels, layerList, layerTree) {
       // JsonReader for the theme selector's config
       var themeSelectorReader = new Ext.data.JsonReader({
            idProperty: 'id',
            root: 'themes',
            fields: [
                {name: 'name', mapping: 'name'},
                {name: 'image', mapping: 'image'}
            ]
        });

        // Store associated to the theme selector Json reader
        var themeStore = new Ext.data.Store({
            reader: themeSelectorReader
        });

        // load data and create listView
        themeStore.loadData(layerList);

        // Template for the theme selector (list view)
        var themeTemplate = new Ext.XTemplate(
            '<p style="padding-top:6px">{[this.getTranslation(values.name)]}</p>',
            {
                compiled: true,
                getTranslation: function (name) {
                     return labels[name];
                 }
            }
        );

        // The theme selector: a list view
        var listView = new Ext.list.ListView({
            id: 'themeListView',
            store: themeStore,
            hideHeaders: true,
            autoWidth: true,
            boxMinWidth: 100,
            expanded: true,
            singleSelect : true,
            flex: 1.0,
            emptyText: 'No images to display',
            reserveScrollOffset: true,
            columns: [
                {
                    header:'icon',
                    width: 0.15,
                    dataIndex: 'image',
                    tpl: '<img src=' + Crdppf.imagesDir + '/themes/{image}'+ ' width=25 height=25></img>'
                },
                {
                    header: 'topic',
                    width: 0.85,
                    dataIndex: 'name',
                    tpl: themeTemplate
                }
                ],
            listeners:{
                click: function(view, index, node, e){
                    layerTree.getRootNode().cascade(function(n) {
                        var ui = n.getUI();
                        ui.toggleCheck(false);
                    });
                    layerTree.getNodeById(themeStore.getAt(index).id).getUI().toggleCheck(true);
                    Ext.getCmp('infoButton').toggle(true);
                    Crdppf.FeaturePanel.setInfoControl();
                }
            }
        });

        // insert listView into a nice looking panel
        this.themePanel = new Ext.Panel({
            id:'themePanel',
            collapsible:true,
            animate:true,
            layout:'fit',
            title:labels.themeSelectorLabel,
            items: listView
        });
    }
};
