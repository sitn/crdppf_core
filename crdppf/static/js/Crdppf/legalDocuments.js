Ext.namespace('Crdppf');

Crdppf.filterlist = {'topic': [], 'layers': [], 'chmunicipalitynb': null, 'cadastrenb': null, 'objectids': []};

Crdppf.docfilters = function (filter) {
    // little helper function to check for the existence of an value in an array
    function isInArray (value, array) {
        return array.indexOf(value) > -1;
    }

    if ('objectids' in filter) {
        if (filter.objectids.length > 0) {
            for (var i = 0; i < filter.objectids.length; i++) {
                if (!(isInArray(filter.objectids[i], Crdppf.filterlist.objectids))) {
                    Crdppf.filterlist.objectids.push(filter.objectids[i]);
                } else {
                    if (isInArray(filter.objectids[i], Crdppf.filterlist.objectids)) {
                        Crdppf.filterlist.objectids.splice(Crdppf.filterlist.objectids.indexOf(filter.objectids[i]), 1);
                    }
                }
            }
        }
    }

    Crdppf.legalDocuments.store.clearFilter();
    Crdppf.legalDocuments.store.filterBy(function (record) {
        // Check if a topic has been selected
        if (Crdppf.filterlist.topic.length > 0) {
            for (var j = 0; j < Crdppf.filterlist.topic.length; j++) {
              // for a given topic, get documents related to a restriction object
              for (var o = 0; o < Crdppf.filterlist.objectids.length; o++) {
                if (record.get('origins').indexOf(Crdppf.filterlist.objectids[o]) > -1) {
                  return record;
                }
              }
            // if the topicid is in the filterlist show the corresponding documents
                if (record.get('origins').indexOf(Crdppf.filterlist.topic[j]) > -1 && Crdppf.filterlist.chmunicipalitynb !== null) {
                    // documents related to a topic and a municipality but no selected object
                    if (record.get('doctype') === 'legalbase' && ((record.get('cadastrenb') === null && record.get('chmunicipalitynb') === null) ||
                        (record.get('chmunicipalitynb') === Crdppf.filterlist.chmunicipalitynb && record.get('cadastrenb') === null) ||
                        (record.get('chmunicipalitynb') === Crdppf.filterlist.chmunicipalitynb &&
                         record.get('cadastrenb') === Crdppf.filterlist.cadastrenb))) {
                      return record;
                    }
                } else if (record.get('origins').indexOf(Crdppf.filterlist.topic[j]) > -1 && Crdppf.filterlist.chmunicipalitynb === null) {
                  return record;
                }
            }
        } else {
          // if no topic is selected display only legal bases
          if (Crdppf.filterlist.topic.length === 0 && record.get('doctype') === 'legalbase') {
              return record;
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
    Crdppf.legalDocuments.store = new Ext.data.Store({
        autoDestroy: true,
        autoLoad: true,
        proxy: proxy,
        remoteSort: true,
        sorters: [{
            property: 'doctype',
            direction: 'ASC'
        }],
        reader: new Ext.data.JsonReader({
            root: 'docs',
            id: 'idobj'
            },
            // definition of the column model
            [
            {name: 'documentid'},
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
            {name: 'sanctiondate', type: 'date'},
            {name: 'abolishingdate', type: 'date'}, // date d'abrogation
            {name: 'entrydate', type: 'date'}, // creation date
            {name: 'publicationdate', type: 'date'},
            {name: 'revisiondate', type: 'date'}, // date de modification
            {name: 'operator'},
            {name: 'origins'}
            // {name: 'validationdate', type:'date'},  //date validation
            // {name: 'modifiedby'},
            // {name: 'status'} //for historization P:provisory, V:valid; A:archived; D:deleted
            ]
        ),
            listeners: {
                load: function () {
                    Crdppf.loadingCounter += 1;
                    Crdppf.triggerFunction(Crdppf.loadingCounter);
                }
            }
    });
};

Crdppf.legalDocuments.createView = function (labels) {

    var legalDocumentsStore = null;

    if (Crdppf.legalDocuments.store.getTotalCount () > 0) {
        // Parse the legal documents and apply the corresponding template
        var templates = new Ext.XTemplate(
            // Bases légales/legal bases
            '<div style="font-family:Arial;padding:5px;">',
                '<h1 class="title" style="margin-bottom:10px;padding-left:10px;font-size:14pt;">'+labels.legalbaseslabel+'</h1>',
                '<div style="font-family:Arial;margin-left:10px;">',
                    '<h2 style="margin-top:10px;margin-bottom:5px;">'+labels.federalLevelTxt+'</h2>',
                    '<tpl for=".">',
                        '<tpl if="this.isLegalbase(doctype) &amp;&amp; this.isFederal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb)">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFFFFF" : "#F5F5F5"]}">',
                                    '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {publicationdate:date("d.m.Y")}</h3>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                        '<tpl if="this.isLegalbase(doctype) &amp;&amp; this.isFederal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb) == false">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFFFFF" : "#F5F5F5"]}">',
                                    '<h3 class="doctitle">{officialtitle} du {publicationdate:date("d.m.Y")}</h3>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                    '</tpl>',

                    '<h2 style="margin-top:10px;margin-bottom:5px;">'+labels.cantonalLevelTxt+'</h2>',
                    '<tpl for=".">',
                        '<tpl if="this.isLegalbase(doctype) &amp;&amp; this.isCantonal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb)">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#F5F5F5"]}"">',
                                    '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {publicationdate:date("d.m.Y")}</h3>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                        '<tpl if="this.isLegalbase(doctype) &amp;&amp; this.isCantonal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb) == false">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#F5F5F5"]}"">',
                                    '<h3 class="doctitle">{officialtitle} du {publicationdate:date("d.m.Y")}</h3>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                    '</tpl>',

                    '<h2 style="margin-top:10px;margin-bottom:5px;">'+labels.municipalityLevelTxt+'</h2>',
                    '<tpl for=".">',
                        '<tpl if="this.isLegalbase(doctype) &amp;&amp; this.isCommunal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb)">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#F5F5F5"]}">',
                                    '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {publicationdate:date("d.m.Y")}</h3>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                        '<tpl if="this.isLegalbase(doctype) &amp;&amp; this.isCommunal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb) == false">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#F5F5F5"]}">',
                                    '<h3 class="doctitle">{officialtitle} du {publicationdate:date("d.m.Y")}</h3>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                        '<tpl if="(values && values.length)">',
                            '<p>Aucun document trouv&eacute; pour cette cat&eacute;gorie</p>',
                        '</tpl>',
                    '</tpl>',
                '</div>',
            '</div>',

            // Dispositions juridiques/legal provisions
            '<div style="font-family:Arial;padding:5px;">',
                '<h1 class="title" style="margin-bottom:10px;padding-left:10px;font-size:14pt;">'+labels.legalprovisionslabel+'</h1>',
                '<div style="font-family:Arial;margin-left:10px;">',
                    '<h2 style="margin-top:10px;margin-bottom:5px;">'+labels.federalLevelTxt+'</h2>',
                    '<tpl for=".">',
                        '<tpl if="this.isLegalprovision(doctype) &amp;&amp; this.isFederal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb)">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFFFFF" : "#F5F5F5"]}">',
                                    '<tpl if="sanctiondate !== null">',
                                        '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                    '</tpl>',
                                    '<tpl if="sanctiondate === null">',
                                        '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle}</h3>',
                                    '</tpl>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                        '<tpl if="this.isLegalprovision(doctype) &amp;&amp; this.isFederal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb) == false">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFFFFF" : "#F5F5F5"]}">',
                                    '<tpl if="sanctiondate !== null">',
                                        '<h3 class="doctitle">{officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                    '</tpl>',
                                    '<tpl if="sanctiondate === null">',
                                        '<h3 class="doctitle">{officialtitle}</h3>',
                                    '</tpl>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                    '</tpl>',

                    '<h2 style="margin-top:10px;margin-bottom:5px;">'+labels.cantonalLevelTxt+'</h2>',
                    '<tpl for=".">',
                        '<tpl if="this.isLegalprovision(doctype) &amp;&amp; this.isCantonal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb)">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFFFFF" : "#F5F5F5"]}"">',
                                    '<tpl if="sanctiondate !== null">',
                                        '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                    '</tpl>',
                                    '<tpl if="sanctiondate === null">',
                                        '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle}</h3>',
                                    '</tpl>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                        '<tpl if="this.isLegalprovision(doctype) &amp;&amp; this.isCantonal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb) == false">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFFFFF" : "#F5F5F5"]}"">',
                                    '<tpl if="sanctiondate !== null">',
                                        '<h3 class="doctitle">{officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                    '</tpl>',
                                    '<tpl if="sanctiondate === null">',
                                        '<h3 class="doctitle">{officialtitle}</h3>',
                                    '</tpl>',
                                    '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                    '</tpl>',

                    '<h2 style="margin-top:10px;margin-bottom:5px;">'+labels.municipalityLevelTxt+'</h2>',
                    '<tpl for=".">',
                        '<tpl if="this.isLegalprovision(doctype) &amp;&amp; this.isCommunal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb)">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFFFFF" : "#F5F5F5"]}">',
                                  '<tpl if="sanctiondate !== null">',
                                      '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                  '</tpl>',
                                  '<tpl if="sanctiondate === null">',
                                      '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle}</h3>',
                                  '</tpl>',
                                  '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                        '<tpl if="this.isLegalprovision(doctype) &amp;&amp; this.isCommunal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb) == false">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFFFFF" : "#F5F5F5"]}">',
                                  '<tpl if="sanctiondate !== null">',
                                      '<h3 class="doctitle">{officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                  '</tpl>',
                                  '<tpl if="sanctiondate === null">',
                                      '<h3 class="doctitle">{officialtitle}</h3>',
                                  '</tpl>',
                                  '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                    '</tpl>',
                '</div>',
            '</div>',

            // references
            '<div style="font-family:Arial;padding:5px;">',
                '<h1 class="title" style="margin-bottom:10px;padding-left:10px;font-size:14pt;">'+labels.referenceslabel+'</h1>',
                '<div style="font-family:Arial;margin-left:10px;">',
                    '<h2 style="margin-top:10px;margin-bottom:5px;">'+labels.federalLevelTxt+'</h2>',
                    '<tpl for=".">',
                        '<tpl if="this.isReference(doctype) &amp;&amp; this.isFederal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb)">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#F5F5F5"]}">',
                                  '<tpl if="sanctiondate !== null">',
                                      '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                  '</tpl>',
                                  '<tpl if="sanctiondate === null">',
                                      '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle}</h3>',
                                  '</tpl>',
                                      '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                        '<tpl if="this.isReference(doctype) &amp;&amp; this.isFederal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb) == false">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#F5F5F5"]}">',
                                  '<tpl if="sanctiondate !== null">',
                                      '<h3 class="doctitle">{officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                  '</tpl>',
                                  '<tpl if="sanctiondate === null">',
                                      '<h3 class="doctitle">{officialtitle}</h3>',
                                  '</tpl>',
                                  '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                    '</tpl>',

                    '<h2 style="margin-top:10px;margin-bottom:5px;">'+labels.cantonalLevelTxt+'</h2>',
                    '<tpl for=".">',
                        '<tpl if="this.isReference(doctype) &amp;&amp; this.isCantonal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb)">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#F5F5F5"]}">',
                                  '<tpl if="sanctiondate !== null">',
                                      '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                  '</tpl>',
                                  '<tpl if="sanctiondate === null">',
                                      '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle}</h3>',
                                  '</tpl>',
                                      '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                        '<tpl if="this.isReference(doctype) &amp;&amp; this.isCantonal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb) == false">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#F5F5F5"]}">',
                                  '<tpl if="sanctiondate !== null">',
                                      '<h3 class="doctitle">{officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                  '</tpl>',
                                  '<tpl if="sanctiondate === null">',
                                      '<h3 class="doctitle">{officialtitle}</h3>',
                                  '</tpl>',
                                  '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                    '</tpl>',

                    '<h2 style="margin-top:10px;margin-bottom:5px;">'+labels.municipalityLevelTxt+'</h2>',
                    '<tpl for=".">',
                        '<tpl if="this.isReference(doctype) &amp;&amp; this.isCommunal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb)">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#F5F5F5"]}">',
                                  '<tpl if="sanctiondate !== null">',
                                      '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                  '</tpl>',
                                  '<tpl if="sanctiondate === null">',
                                      '<h3 class="doctitle"><a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{officialnb}</a> - {officialtitle}</h3>',
                                  '</tpl>',
                                      '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
                        '</tpl>',
                        '<tpl if="this.isReference(doctype) &amp;&amp; this.isCommunal(state, municipalityname) &amp;&amp; this.isOfficialnb(officialnb) == false">',
                            '<tpl for=".">',
                                '<div style="font-size:10pt;padding:5px 15px;background-color:{[xindex % 2 === 0 ? "#FFF" : "#F5F5F5"]}">',
                                  '<tpl if="sanctiondate !== null">',
                                      '<h3 class="doctitle">{officialtitle} du {sanctiondate:date("d.m.Y")}</h3>',
                                  '</tpl>',
                                  '<tpl if="sanctiondate === null">',
                                      '<h3 class="doctitle">{officialtitle}</h3>',
                                  '</tpl>',
                                  '<p class="docurl"><b>URL:</b> <a href="#" onClick="window.open(\'{remoteurl}\');" target="_blank">{remoteurl}</a></p>',
                                '</div>',
                            '</tpl>',
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
                isFederal: function(state){
                    return state === null;
                },
                isCantonal: function(state, municipalityname){
                    return state !== null && (municipalityname === null || municipalityname === '');
                },
                isCommunal: function(state, municipalityname){
                    return state !== null && municipalityname !== null;
                },
                isOfficialnb: function(officialnb){
                    return officialnb !== null;
                }
            }
        );

        legalDocumentsStore = this.store;

    } else {
        var nodocs = ('<div style="font-family:Arial;padding:5px;">'+
        '<h1 class="title" style="margin-bottom:10px;padding-left:10px;font-size:14pt;">'+labels.legalbaseslabel+'</h1>'+
            '<div style="font-family:Arial;margin-left:10px;">'+
                '<h2 style="margin-top:10px;margin-bottom:5px;">'+labels.noDocumentsTxt+'</h2>'+
            '</div>'+
        '</div>');
    }

      // Create the legal information container
    var legalInfo = new Ext.DataView({
        title: labels.legalBasisTab,
        store: legalDocumentsStore,
        tpl: templates,
        autoHeight: true,
        multiSelect: true,
        emptyText: labels.noDocumentsTxt
    });

    return legalInfo;

};
