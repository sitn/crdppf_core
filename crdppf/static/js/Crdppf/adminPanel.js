/*
ONLY reference scripts here, if they should be compiled in the build for faster loading
not really needed for admin stuff as the server should respond fast enough...
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

    // create the header panel containing the page banner
    var headerPanel = new Ext.Panel({
        region: 'north',
        height: 55,
        border: false,
        contentEl: 'header'
    });

    // Container for the content display
    contentPanel = new Ext.Panel({
        autoScroll: true,
        items:[
            Crdppf.translationsPanel(Crdppf.labels)
        ]
    });
    
    // Container for the map and legal documents display
    centerPanel = new Ext.Panel({
        region: 'center',
        autoScroll: true,
        items:[
            Crdppf.adminToolbar(Crdppf.labels),
            contentPanel
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
	Ext.EventManager.onWindowResize(crdppf.doLayout,crdppf);
});
