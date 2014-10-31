Ext.namespace('Crdppf');

// create translations grid panel
Crdppf.translationsPanel = function(labels) {
    
    var translationsgrid = new Ext.grid.GridPanel();
    
    // configure whether filter query is encoded or not (initially)
    var encode = true;
    
    var translationsproxy = new Ext.data.HttpProxy({url: Crdppf.getTranslationListUrl});

    var myPageSize = 30;  // server script should only send back 30 items at a time
        
    // definition of the data store containing the translations
    var translationsstore=new Ext.data.Store({
        proxy: translationsproxy,
        remoteSort: true,
        baseParams:{
          start: 0,          
          limit: myPageSize
        },
        sorters: [{
            property: 'id',
            direction: 'DESC'
        }],
        reader: new Ext.data.JsonReader({
            root:'translations',
            totalProperty: 'totalCount',
            id:'id'
            },
            //definition of the columns to fetch in the DB
            [
            {name: 'id', type: 'numeric'},
            {name: 'varstr'},
            {name: 'de'},
            {name: 'fr'},
            {name: 'it'},
            {name: 'ro'},
            {name: 'en'}         
            ]
        )
    });
    translationsstore.setDefaultSort('id', 'ASC');

    var filters = new Ext.ux.grid.GridFilters({
        // encode and local configuration options defined previously for easier reuse
        encode: encode, // json encode the filter query
        local: false,   // defaults to false (remote filtering)
        filters: [{
            type: 'numeric',
            dataIndex: 'id'
        },{
            type: 'string',
            dataIndex: 'varstr'
        },{
            type: 'string',
            dataIndex: 'de'
        },{
            type: 'string',
            dataIndex: 'fr'
        },{
            type: 'string',
            dataIndex: 'it'
        },{
            type: 'string',
            dataIndex: 'ro'
        },{
            type: 'string',
            dataIndex: 'en'
        }]
    }); 
    
    // load previously defined data source
    translationsstore.load({
        // specify params for the first page load if using paging
        params:{
          start: 0,          
          limit: myPageSize
        }
    });
    
    // Definition of the column model for grid representation
    var colModel = new Ext.grid.ColumnModel([
        {header: "Id", width: 30, dataIndex: 'id', sortable: true, filtrable: true},
        {header: "Nom de la variable", width: 50, dataIndex: 'varstr', sortable: true, filtrable: true},
        {header: "Deutsch", width: 50, dataIndex: 'de', sortable: true, filtrable: true},
        {header: "Français", width: 50, dataIndex: 'fr', sortable: true, filtrable: true},
        {header: "Italiano", width: 50, dataIndex: 'it', sortable: true, filtrable: true},
        {header: "Rumantsch", width: 50, dataIndex: 'ro', sortable: true, filtrable: true},
        {header: "English", width: 50, dataIndex: 'en',  sortable: true, filtrable: true}
    ]);
    
    var translationpanel = new Ext.grid.GridPanel({
        layout: 'fit',
        border: false,
        store: translationsstore,
        title: 'Liste des traductions',
        cm: colModel,
        // customize view config
        plugins: [filters],
        viewConfig: {
            forceFit:true
        },
        bbar: new Ext.PagingToolbar({
                pageSize: myPageSize,
                store: translationsstore,       // grid and PagingToolbar using same store
                displayInfo: true,
                pageSize: myPageSize,
                displayMsg: 'Traductions {0} - {1} de {2}',
                emptyMsg: "Pas de résultat trouvé"
        })
    });

    
    //pass along browser window resize events to the panel
    Ext.EventManager.onWindowResize(translationpanel.doLayout, translationpanel);
    
    return translationpanel;
    
};
