Ext.namespace('Crdppf');

/***
*create layer tree and append nodes & subnodes to it
***/
Crdppf.adminToolbar = function(labels) {

    var toolbar = new Ext.Toolbar();

        toolbar.add({
                text: labels.adminMenuApplicationLabel,
                iconCls: 'crdppf_application_menu',
                menu: {
                    xtype: 'menu',
                    plain: true,
                    items:[{
                        text: labels.adminMenuAppConfigTxt,
                        handler: function() {
                            window.location = 'configpanel';
                        }
                    },{
                        text: labels.adminMenuGetTranslationsTxt,
                        handler: function() {
                            window.location = 'get_translations';
                        }
                    },{
                        text: labels.adminMenuGetLayersTxt,
                        handler: function() {
                            window.location = 'get_layers';
                        }
                    }]
                }
            },'-',{
                text: labels.adminMenuDocumentLabel,
                iconCls: 'crdppf_documents_menu',
                menu: {
                    xtype: 'menu',
                    plain: true,
                    items: [{
                        text: labels.adminMenuCreateNewDocumentTxt,
                        handler: function() {
                            window.location = 'formulaire_reglements';
                        }
                    },{
                        text: labels.adminMenuEditDocumentReferencesTxt,
                        handler: function() {
                            window.location = 'get_doclist';
                        }
                    }]
                }
            },'-',{
                text: labels.adminMenuPDFLabel,
                iconCls: 'crdppf_extract_menu',
                menu: {
                    xtype: 'menu',
                    plain: true,
                    items:[{
                        text: labels.adminMenuConfigurePdfExtractTxt,
                        handler: function() {
                            window.location = 'get_pdfconfig';
                        }
                    },{
                        text: labels.adminMenuConfigureSLDTxt,
                        handler: function() {
                            window.location = 'get_SLD';
                        }
                    }]
                }
            },'-',{
                text: labels.adminMenuOpenlayersLabel,
                iconCls: 'crdppf_openlayers_menu',
                menu: {
                    xtype: 'menu',
                    plain: true,
                    items:[{
                        text: labels.adminMenuConfigureOLTxt,
                        handler: function() {
                            window.location = 'get_OLconfig';
                        }
                    }]
                }
            },'-',{
                text: labels.adminMenuHomeButtonLabel,
                iconCls: 'crdppf_menu_home',
                handler: function() {
                    if (document.URL == '/') {
                        alert(adminMenuHomeButtonTxt);
                        return;
                    }
                    window.location = '/';
                }
            }
        );
        toolbar.doLayout();

    return toolbar;
};
