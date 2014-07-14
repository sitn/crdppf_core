Ext.namespace('Crdppf');

Crdppf.legalDocuments = function(labels) {
/*
Function to collect all legal documents related to a selection of restrictions from the db
and create a data view applying a template to format the page layout
TODO: pass topic and layerfk to the function to request only related docs
*/
        var legaldocs = new Ext.data.JsonStore({
        autoDestroy: true,
        autoLoad: true,
        url: Crdppf.getLegalDocumentsUrl,
        sort: {
            field: 'doctype',
            direction: 'ASC'
        },
        idProperty: 'documentid',
        fields:[
            {name: 'documentid', type:'integer'},
            {name: 'doctype'},
            {name: 'numcom'},
            {name: 'numcad'},
            {name: 'topicfk'},
            {name: 'title'},
            {name: 'officialtitle'},
            {name: 'abreviation'}, 
            {name: 'officialnb'},
            {name: 'canton'},
            {name: 'commune'},
            {name: 'lang'},
            {name: 'permalink'},
            {name: 'localurl'},
            {name: 'documenturl'},
            //{name: 'remoteurl'},
            {name: 'legalstate'},
            {name: 'enteredby'},
            {name: 'digitalisationdate', type:'date'}, // date saisie
            //{name: 'publicationdate', type:'date'}, 
            {name: 'publishedsince', type:'date'}, 
            {name: 'validationdate', type:'date'},  //date sanction
            {name: 'modificationdate', type:'date'}, //date de modification
            {name: 'modifiedby'},
            {name: 'abolishingdate', type:'date'}, //date d'abrogation
			{name: 'status'} //for historization P:provisory, V:valid; A:archived; D:deleted
        ]
    });

    // Parse the legal documents and apply the corresponding template
    var templates = new Ext.XTemplate(
   // Bases légales/legal bases
  '<div style="font-family:Arial;padding:5px;">',
    '<h1 class="title" style="margin-bottom:10px;padding-left:10px;font-size:14pt;">Bases légales</h1>',
  	'<div style="font-family:Arial;margin-left:10px;">',
  	'<h2 style="margin-top:10px;margin-bottom:5px;">Niveau fédéral</h2>',
		'<tpl for=".">',
			'<tpl if="this.isLegalbase(doctype) &amp;&amp; this.isFederal(canton, commune)">',
        		'<tpl for=".">',
                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                    '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {publishedsince:date("d.m.Y")}</h3>',
                    '<p class="docurl">URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                '</div>',
                '</tpl>',
        	'</tpl>',
    	'</tpl>',

  '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau cantonal</h2>',
		'<tpl for=".">',
        	'<tpl if="this.isLegalbase(doctype) &amp;&amp; this.isCantonal(canton, commune)">',
        			'<tpl for=".">',
                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}"">',
                    '<p class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle}</b><b style="padding-left:25px;">Date de publication:</b> {publishedsince:date("d.m.Y")}</p>',
                    '<p class="docurl">URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                '</div>',
    		'</tpl>',
    	'</tpl>',
    	
		'<tpl for=".">',
        	'<tpl if="this.isLegalbase(doctype) &amp;&amp; this.isCommunal(canton, commune)">',
  			'<h2 style="margin-top:10px;margin-bottom:5px;">Niveau communal</h2>',
        		'<tpl for=".">',
                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                    '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle}<span style="padding-left:15px;">Date de publication:</b> {publishedsince:date("d.m.Y")}<span></h3>',
                    '<p class="docurl">URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                    '<br />',
                '</div>',
                '</tpl>',
                '</tpl>',
    		'</tpl>',
    	'</tpl>',
    	'</div>',
    '</div>',
    
   // Dispositions légales/legal provisions
  '<div style="font-family:Arial;padding:5px;">',
    '<h1 class="title" style="margin-bottom:10px;padding-left:10px;font-size:14pt;;">Dispositions juridiques</h1>',
  	'<div style="font-family:Arial;margin-left:10px;">',
  	'<h2 style="margin-top:10px;margin-bottom:5px;">Niveau fédéral</h2>',
		'<tpl for=".">',
        	'<tpl if="this.isLegalprovision(doctype) &amp;&amp; this.isFederal(canton)">',
                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                    '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle}<span style="padding-left:15px;">Date de publication:</b> {publishedsince:date("d.m.Y")}<span></h3>',
                    '<p class="docurl">URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                    '<br />',
                '</div>',
        	'</tpl>',
    	'</tpl>',

  '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau cantonal</h2>',
		'<tpl for=".">',
        	'<tpl if="this.isLegalprovision(doctype) &amp;&amp; this.isCantonal(canton, commune)">',
                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                    '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle}<span style="padding-left:15px;">Date de publication:</b> {publishedsince:date("d.m.Y")}<span></h3>',
                    '<p class="docurl">URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                    '<br />',
                '</div>',
    		'</tpl>',
    	'</tpl>',
    	
  '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau communal</h2>',
		'<tpl for=".">',
        	'<tpl if="this.isLegalprovision(doctype) &amp;&amp; this.isCommunal(canton, commune)">',
                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                    '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle}<span style="padding-left:15px;">Date de publication:</b> {publishedsince:date("d.m.Y")}<span></h3>',
                    '<p class="docurl">URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                    '<br />',
                '</div>',
    		'</tpl>',
    	'</tpl>',
    	'</div>',
    '</div>',
	{
        // member functions:
        isLegalbase: function(doctype){
            return doctype == 'legalbase';
        },
        isLegalprovision: function(doctype){
            return doctype == 'legalprovision';
        },
        isReference: function(doctype){
            return doctype == 'reference';
        },
        isOther: function(doctype){
            return doctype == 'other';
        },
        isFederal: function(canton){
            return canton == null;
        },
        isCantonal: function(canton, commune){
            return canton != null && commune == null;
        },
        isCommunal: function(canton, commune){
            return canton != null && commune != null;
	    }
	}
    );


    // Create the legal information container
    var legalInfo = new Ext.DataView({
        title: labels.legalBasisTab,
        store: legaldocs,
        tpl: templates,
        autoHeight: true,
        multiSelect: true,
        //overClass: 'x-view-over', - not used yet, might be nice so I leave it for now
        emptyText: 'No legal documents to display'
    });

    return legalInfo;

};

