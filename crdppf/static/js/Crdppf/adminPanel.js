/*
ONLY reference scripts here, if they should be compiled in the build for faster loading
not really needed for admin stuff as the server should respond fast enough...
 */

// MAIN USER INTERFACE
Ext.onReady(function() {
    
    Ext.namespace('Crdppf');
    Crdppf.labels = '' ;

    loadingCounter = 0;
    
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
            loadingCounter += 1;
            triggerFunction(loadingCounter);   
        },
        method: 'POST',
        failure: function () {
            Ext.Msg.alert(Crdppf.labels.serverErrorMessage);
        }
    });

    var triggerFunction = function(counter) {
        if (counter == 1) {
    
        // create the header panel containing the page banner
        var headerPanel = new Ext.Panel({
            region: 'north',
            height: 55,
            border: false,
            contentEl: 'header'
        });
      
        // Container for the map and legal documents display
        var contentPanel = new Ext.Panel({
            region: 'center',
            margins: '5 5 0 0',
            layout: 'fit',
            items: [
                Crdppf.translationsPanel(Crdppf.labels)
            ],
            tbar: Crdppf.adminToolbar(Crdppf.labels)
        });
            
        // Main window layout
        var crdppf = new Ext.Viewport({
            layout: 'border',
            renderTo:'main',
            id:'viewPort',
            border:true,
            items: [
                headerPanel,
                contentPanel
            ]
        });
            
        // Redo the layout if window is resized
        //pass along browser window resize events to the panel
        Ext.EventManager.onWindowResize(crdppf.doLayout,crdppf);
        }
    };
});
