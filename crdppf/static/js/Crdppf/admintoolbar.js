Ext.onReady(function(){

    Ext.QuickTips.init();
   // turn on validation errors beside the field globally
    Ext.form.Field.prototype.msgTarget = 'side';

    var bd = Ext.getBody();
    
    var tb = new Ext.Toolbar();
    tb.render('tbar');

    tb.add({
            text:'Application',
            iconCls: 'geoshop_menu_order',
            menu: {
                xtype: 'menu',
                plain: true,
                items:[{
                    text: 'Configuration de l\'application',
                    handler: function() {
                        window.location = "${request.route_url('get_configuration')}";
                    }
                },{
                    text: 'Afficher les traductions',
                    handler: function() {
                        window.location = "${request.route_url('get_translations')}";
                    }
                },{
                    text: 'Afficher les couches',
                    handler: function() {
                        window.location = "${request.route_url('get_layers')}";
                    }
                }]
            }
        },'-',{
            text: 'Documents',
            iconCls: 'geoshop_menu_user',
            menu: {
                xtype: 'menu',
                plain: true,
                items: [{
                    text: 'Gestion des documents',
                    handler: function() {
                        window.location = "${request.route_url('get_documents')}";
                    }
                },{
                    text: 'Gestion des comptes',
                    handler: function() {
                        window.location = "${request.route_url('userlist')}";
                    }
                }]
            }
        },'-',{
            text: 'Extrait PDF',
            iconCls: 'geoshop_menu_invoice',
            handler: function() {
                window.location = "${request.route_url('billing')}";
            }
        },'-',{
            text: 'Retour au portail CRDPPF',
            iconCls: 'geoshop_menu_geoshop',
            handler: function() {
                if (document.URL == "${request.route_url('home')}") {
                    alert('Mais, t\'es déjà sur le CRDPPF...');
                    return;
                }
                window.location = "${request.route_url('home')}";
            }
        }
    );
    
    tb.doLayout();

    
});