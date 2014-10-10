/*
 * @include Crdppf/adminToolbar.js
 * @include Crdppf/legalDocuments.js
 * @include Crdppf/measureTools.js
 */

var layerList;

// MAIN USER INTERFACE
Ext.onReady(function() {
    
    Ext.namespace('Crdppf');
    Crdppf.labels = '' ;
    
    // set the application language to the user session settings
    var lang = ''; // The current session language

    // Get the current session language
    Ext.Ajax.request({
        url: Crdppf.getLanguageUrl,
        success: function(response) {
            var lang_json = Ext.decode(response.responseText);
            lang = lang_json['lang'];
            //OpenLayers.Lang.setCode(lang);
            //~ if (lang !== '' && lang == 'Fr'){
                //~ OpenLayers.Util.extend(OpenLayers.Lang.fr, Crdppf.labels);
            //~ } else if (lang !== '' && lang == 'De') {
                //~ OpenLayers.Util.extend(OpenLayers.Lang.de, Crdppf.labels);
            //~ } else if (lang !== '' && lang == 'en') {
                //~ OpenLayers.Util.extend(OpenLayers.Lang.en, Crdppf.labels);
            //~ } else if (lang !== '') {
                //~ OpenLayers.Util.extend(OpenLayers.Lang.fr, Crdppf.labels);
            //~ }
            //~ loadingCounter += 1;
            //~ triggerFunction(loadingCounter);            
        },
        method: 'POST',
        failure: function () {
            Ext.Msg.alert(Crdppf.labels.serverErrorMessage);
        }
    }); 
    
    // Load the interface's Crdppf.labels
    Ext.Ajax.request({
        url: Crdppf.getTranslationDictionaryUrl,
        success: function(response) {
            Crdppf.labels = Ext.decode(response.responseText);
        },
        method: 'POST',
        failure: function () {
            Ext.Msg.alert(Crdppf.labels.serverErrorMessage);
        }
    });

    //~ // set the lang parameter in session when selected through the language buttons
    //~ function setLanguage(value){
        //~ var request = OpenLayers.Request.GET({
            //~ url: Crdppf.setLanguageUrl,
            //~ params: {
                //~ lang:value,
                //~ randomkey: Math.random()
            //~ },
            //~ proxy: null,
            //~ async: false
        //~ });
        //~ window.location.reload();
    //~ }


    // create the header panel containing the page banner
    var headerPanel = new Ext.Panel({
        region: 'north',
        height: 55,
        border: false,
        contentEl: 'header'
    });

    adminToolbar =  new Ext.Toolbar({
        autoWidth: true,
        height: 20,
        html: 'toolbar'
    });
    
    // Container for the map and legal documents display
    centerPanel = new Ext.Panel({
        region: 'center',
        autoScroll: true,
        items:[
            adminToolbar //,Crdppf.legalDocuments(Crdppf.labels)
        ]
    });
    
    // Main window layout
    var crdppf = new Ext.Viewport({
        layout: 'border',
        renderTo:'main',
        id:'viewPort',
        border:true,
        items: [
            headerPanel,
            centerPanel
        ]
    });
  
	// Refait la mise en page si la fenêtre change de taille
	//pass along browser window resize events to the panel
	//Ext.EventManager.onWindowResize(crdppf.doLayout,crdppf);
});
