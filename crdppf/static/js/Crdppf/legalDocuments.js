Ext.namespace('Crdppf');

Crdppf.filterlist = {'theme':[], 'topic' : [], 'municipalitynb': 0};

Crdppf.docfilters = function(filter) {

    function isInArray(value, array) {
        return array.indexOf(value) > -1;
    }

    // if a topicid is passed in the filter, check if it exists already in the array
    // if not, add it - else remove it
    if ('topicfk' in filter) {
        if (filter['topicfk']) {
            for (key in filter['topicfk']){
                if (filter['topicfk'][key] == true) {
                    // function to add a filter criteria
                    if ( !(isInArray(key, Crdppf.filterlist['topic']))){
                        Crdppf.filterlist['topic'].push(key);
                    }
                } else {
                    if (isInArray(key, Crdppf.filterlist['topic'])){
                        Crdppf.filterlist['topic'].splice(Crdppf.filterlist['topic'].indexOf(key), 1);
                    }
                }
            }
        }
    }
    
    if ('municipalitynb' in filter) {
        if (filter['municipalitynb'] > 0) {
            Crdppf.filterlist['municipalitynb'] = filter['municipalitynb'];
        } else {
            Crdppf.filterlist['municipalitynb'] = 0;
        }
    }

    Crdppf.legalDocuments.store.clearFilter();
    Crdppf.legalDocuments.store.filterBy(function (record) {
        if (Crdppf.filterlist['municipalitynb'] > 0){
            if (record.get('numcad') == Crdppf.filterlist['municipalitynb'] || record.get('numcad') == 0) {
                for (var i = 0; i < Crdppf.filterlist['topic'].length; i++){
                // if the topicid is in the filterlist show the corresponding documents
                 if (record.get('topicfk') == Crdppf.filterlist['topic'][i].toString()) return record;
                }
            }
        } else {
            for (var i = 0; i < Crdppf.filterlist['topic'].length; i++){
            // if the topicid is in the filterlist show the corresponding documents
             if (record.get('topicfk') == Crdppf.filterlist['topic'][i].toString()) return record;
            }
        }
    });
    return Crdppf.filterlist;
};
    

Crdppf.legalDocuments = function() {
    /*
    Function to collect all legal documents related to a selection of restrictions from the db
    and create a data view applying a template to format the page layout
    TODO: pass topic and layerfk to the function to request only related docs
    */

    var proxy = new Ext.data.HttpProxy({
        url: Crdppf.getLegalDocumentsUrl
    });
        
    // definition of datastore
    Crdppf.legalDocuments.store =  new Ext.data.Store({
        autoDestroy: true,
        autoLoad: true,
        proxy: proxy,
        remoteSort: true,
        sorters: [{
            property: 'documentid',
            direction: 'ASC'
        }],
        reader: new Ext.data.JsonReader({
            root:'docs',
            id:'idobj'
            },
            // definition of the column model
            [
            {name: 'docid'},
            {name: 'doctype'},
            {name: 'lang'},
            {name: 'state'},
            {name: 'chmunicipalitynb', type: 'numeric'},
            {name: 'municipalitynb', type: 'numeric'},
            {name: 'municipalityname'},
            {name: 'cadastrenb', type: 'numeric'},
            {name: 'title'},
            {name: 'officialtitle'},
            {name: 'abbreviation'}, 
            {name: 'officialnb'},
            {name: 'remoteurl'},
            {name: 'localurl'},
            {name: 'legalstate'},
            {name: 'sanctiondate', type:'date'},
            {name: 'abolishingdate', type:'date'}, //date d'abrogation
            {name: 'entrydate', type:'date'}, // creation date
            {name: 'publicationdate', type:'date'},
            {name: 'revisiondate', type:'date'}, //date de modification
            {name: 'operator'}, 
            //{name: 'validationdate', type:'date'},  //date validation
            //{name: 'modifiedby'},
            //{name: 'status'} //for historization P:provisory, V:valid; A:archived; D:deleted      
            ]
        ), 
            listeners:{
                load: function() {
                    Crdppf.loadingCounter += 1;
                    //console.log(Crdppf.legalDocuments.store);
                }
            }
    });
};


Crdppf.legalDocuments.createView = function(labels) {

    if (Crdppf.legalDocuments.store.getTotalCount()> 0) {
        // Parse the legal documents and apply the corresponding template
        var templates = new Ext.XTemplate(
        // Bases légales/legal bases
        '<div style="font-family:Arial;padding:5px;">',
            '<h1 class="title" style="margin-bottom:10px;padding-left:10px;font-size:14pt;">Bases légales</h1>',
                '<div style="font-family:Arial;margin-left:10px;">',
                    '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau fédéral</h2>',
                    '<tpl for=".">',
                        '<tpl if="this.isLegalbase(doctype) &amp;&amp; this.isFederal(state, municipalityname)">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                                    '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                    '</tpl>',

                    '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau cantonal</h2>',
                    '<tpl for=".">',
                        '<tpl if="this.isLegalbase(doctype) &amp;&amp; this.isCantonal(state, municipalityname)">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}"">',
                                    '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
            
                    '<tpl for=".">',
                        '<tpl if="this.isLegalbase(doctype) &amp;&amp; this.isCommunal(state, municipalityname)">',
                            '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau communal</h2>',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                                    '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
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
                    '<tpl if="this.isLegalprovision(doctype) &amp;&amp; this.isFederal(state)">',
                        '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                            '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                            '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                            '<br />',
                        '</div>',
                    '</tpl>',
                '</tpl>',

                '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau cantonal</h2>',
                '<tpl for=".">',
                    '<tpl if="this.isLegalprovision(doctype) &amp;&amp; this.isCantonal(state, municipalityname)">',
                        '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                            '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                            '<p class="docurl">URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                            '<br />',
                        '</div>',
                    '</tpl>',
                '</tpl>',
    
                '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau communal</h2>',
                '<tpl for=".">',
                    '<tpl if="this.isLegalprovision(doctype)">',
                        '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                            '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                            '<p class="docurl">URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                            '<br />',
                        '</div>',
                    '</tpl>',
                '</tpl>',
            '</div>',
        '</div>',

        // references
        '<div style="font-family:Arial;padding:5px;">',
            '<h1 class="title" style="margin-bottom:10px;padding-left:10px;font-size:14pt;;">Renvois et informations</h1>',
            '<div style="font-family:Arial;margin-left:10px;">',
                '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau fédéral</h2>',
                '<tpl for=".">',
                    '<tpl if="this.isReference(doctype) &amp;&amp; this.isFederal(state)">',
                        '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                            '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                            '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                            '<br />',
                        '</div>',
                    '</tpl>',
                '</tpl>',

                '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau cantonal</h2>',
                '<tpl for=".">',
                    '<tpl if="this.isReference(doctype) &amp;&amp; this.isCantonal(state, municipalityname)">',
                        '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                            '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                            '<p class="docurl">URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                            '<br />',
                        '</div>',
                    '</tpl>',
                '</tpl>',
            
                '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau communal</h2>',
                '<tpl for=".">',
                    '<tpl if="this.isReference(doctype)">',
                        '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                            '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                            '<p class="docurl">URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                            '<br />',
                        '</div>',
                    '</tpl>',
                '</tpl>',
            '</div>',
        '</div>',

        // temporary provisions
        '<div style="font-family:Arial;padding:5px;">',
            '<h1 class="title" style="margin-bottom:10px;padding-left:10px;font-size:14pt;;">Dispositions transitoires</h1>',
            '<div style="font-family:Arial;margin-left:10px;">',
                '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau fédéral</h2>',
                '<tpl for=".">',
                    '<tpl if="this.isTemporaryprovision(doctype) &amp;&amp; this.isFederal(state)">',
                        '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                            '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                            '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                            '<br />',
                        '</div>',
                    '</tpl>',
                '</tpl>',

                '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau cantonal</h2>',
                '<tpl for=".">',
                    '<tpl if="this.isTemporaryprovision(doctype) &amp;&amp; this.isCantonal(state, municipalityname)">',
                        '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                            '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                            '<p class="docurl">URL:</b> <a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{documenturl}</a></p>',
                            '<br />',
                        '</div>',
                    '</tpl>',
                '</tpl>',

                '<h2 style="margin-top:10px;margin-bottom:5px;">Niveau communal</h2>',
                '<tpl for=".">',
                    '<tpl if="this.isTemporaryprovision(doctype)">',
                        '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#EEE"]}">',
                            '<h3 class="doctitle"><a href="#" onClick="window.open(\'{documenturl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
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
            isTemporaryprovision: function(doctype){
                return doctype == 'temporaryprovision';
            },
            isReference: function(doctype){
                return doctype == 'reference';
            },
            isOther: function(doctype){
                return doctype == 'other';
            },
            isFederal: function(state){
                return state == null;
            },
            isCantonal: function(state, municipalityname){
                return state != null && municipalityname == null;
            },
            isCommunal: function(state, municipalityname){
                return state != null && municipalityname != null;
            }
        }
        );
             
        // Create the legal information container
        var legalInfo = new Ext.DataView({
            title: labels.legalBasisTab,
            store: this.store,
            tpl: templates,
            autoHeight: true,
            multiSelect: true,
            //overClass: 'x-view-over', - not used yet, might be nice so I leave it for now
            emptyText: labels.noDocumentsTxt
        });
          
    } else {
        var nodocs = ('<div style="font-family:Arial;padding:5px;">'+
        '<h1 class="title" style="margin-bottom:10px;padding-left:10px;font-size:14pt;">Documents légaux</h1>'+
            '<div style="font-family:Arial;margin-left:10px;">'+
                '<h2 style="margin-top:10px;margin-bottom:5px;">Pour cette séléction aucun document n\'a été trouvé.</h2>'+
            '</div>'+
        '</div>');

        // Create the legal information container
        var legalInfo = new Ext.DataView({
            title: labels.legalBasisTab,
            html: nodocs,
            autoHeight: true,
            multiSelect: true,
            //overClass: 'x-view-over', - not used yet, might be nice so I leave it for now
            emptyText: labels.noDocumentsTxt
        });

    };

    return legalInfo;
                
};

