Ext.onReady(function(){

    Ext.QuickTips.init();
   // turn on validation errors beside the field globally
    Ext.form.Field.prototype.msgTarget = 'side';

    var bd = Ext.getBody();
    
    var tb = new Ext.Toolbar();
    tb.render('tbar');

    tb.add({
            text:'Application',
            iconCls: 'crdppf_application_menu',
            menu: {
                xtype: 'menu',
                plain: true,
                items:[{
                    text: 'Configuration de l\'application',
                    handler: function() {
                        window.location = 'get_configpanel';
                    }
                },{
                    text: 'Afficher les traductions',
                    handler: function() {
                        window.location = 'get_translations';
                    }
                },{
                    text: 'Afficher les couches',
                    handler: function() {
                        window.location = 'get_layers';
                    }
                }]
            }
        },'-',{
            text: 'Documents',
            iconCls: 'crdppf_documents_menu',
            menu: {
                xtype: 'menu',
                plain: true,
                items: [{
                    text: 'Saisir un document',
                    handler: function() {
                        window.location = 'formulaire_reglements';
                    }
                },{
                    text: 'Gestion des references',
                    handler: function() {
                        window.location = 'get_doclist';
                    }
                }]
            }
        },'-',{
            text: 'Extrait PDF',
            iconCls: 'crdppf_extract_menu',
            menu: {
                xtype: 'menu',
                plain: true,
                items:[{
                    text: 'Configuration de l\'extrait',
                    handler: function() {
                        window.location = 'get_pdfconfig';
                    }
                },{
                    text: 'Configuration de la SLD',
                    handler: function() {
                        window.location = 'get_SLD';
                    }
                }]
            }
        },'-',{
            text: 'Retour au portail CRDPPF',
            iconCls: 'geoshop_menu_geoshop',
            handler: function() {
                if (document.URL == "${request.route_url('home')}") {
                    alert('Mais, t\'es déjà sur le CRDPPF...');
                    return;
                }
                window.location = 'home';
            }
        }
    );
    
    tb.doLayout();

    
});