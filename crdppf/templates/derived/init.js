if(!window.Crdppf) Crdppf = {};

//~ Crdppf.setLanguageUrl = "${request.route_url('set_language')}";
//~ Crdppf.getLanguageUrl = "${request.route_url('get_language')}";
//~ Crdppf.getTranslationDictionaryUrl = "${request.route_url('get_translation_dictionary')}";
//~ Crdppf.getTranslationListUrl = "${request.route_url('get_translations_list')}";
//~ Crdppf.getBaselayerConfigUrl = "${request.route_url('get_baselayers_config')}";


// MAIN USER INTERFACE
//~ Ext.onReady(function() {
    
    //~ Ext.namespace('Crdppf');
    Crdppf.labels = '' ;
    ${crdppf_fr_car}
    // Load the interface's Crdppf.labels
    //~ Ext.Ajax.request({
        //~ url: Crdppf.getTranslationDictionaryUrl,
        //~ success: function(response) {
            //~ Crdppf.labels = Ext.decode(response.responseText);         
        //~ },
        //~ method: 'POST',
        //~ failure: function () {
            //~ Ext.Msg.alert(Crdppf.labels.serverErrorMessage);
        //~ }
    //~ });
    
//~ });
