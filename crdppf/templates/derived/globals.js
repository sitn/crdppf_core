if(!window.Crdppf) Crdppf = {};

Crdppf.baseUrl = "${request.route_url('home')}";
Crdppf.imagesDir = "${request.route_url('images')}";
Crdppf.staticImagesDir = "${request.route_url('catchall_static', subpath='proj/images/')}";
Crdppf.getFeatureUrl = "${request.route_url('get_features')}";
Crdppf.setLanguageUrl = "${request.route_url('set_language')}";
Crdppf.getLanguageUrl = "${request.route_url('get_language')}";
Crdppf.getTranslationDictionaryUrl = "${request.route_url('get_translation_dictionary')}";
Crdppf.getTranslationListUrl = "${request.route_url('get_translations_list')}";
Crdppf.getLegalDocumentsUrl = "${request.route_url('getLegalDocuments')}";
Crdppf.getInterfaceConfigUrl = "${request.route_url('get_interface_config')}";
Crdppf.getBaselayerConfigUrl = "${request.route_url('get_baselayers_config')}";
Crdppf.wmsUrl = "${request.route_url('ogcproxy')}";
Crdppf.ogcproxyUrl  = "${request.route_url('ogcproxy')}";
Crdppf.printUrl = "${request.route_url('create_extract')}";
<%
    print_report = request.route_url('printproxy_report_create', idemai='', type_='2split')
    print_report = print_report.split('2split')[0]
    print_status = request.route_url('printproxy_status', ref='')
    print_status = print_status.split('.json')[0]
%>
Crdppf.printReportCreateUrl = "${print_report}";
Crdppf.printReportStatusUrl = "${print_status}";
Crdppf.printReportGetUrl = "${request.route_url('printproxy_report_get', ref='')}";
Crdppf.fulltextsearchUrl = "${request.registry.settings['fulltextsearch_url']}";
Crdppf.mapproxyUrl = [${request.registry.settings['mapproxyurl']|n}];
Crdppf.mapExtent = [${request.registry.settings['mapExtent']|n}];
Crdppf.mapMaxExtent= [${request.registry.settings['mapMaxExtent']|n}];
Crdppf.mapCenter = [${request.registry.settings['mapCenter']|n}];
Crdppf.mapSRS = "${request.registry.settings['mapSRS']}";
Crdppf.mapMatrixSet = "${request.registry.settings['mapMatrixSet']}";
Crdppf.mapResolutions = [${request.registry.settings['mapResolutions']|n}];
Crdppf.mapOverviewExtent = [${request.registry.settings['mapOverviewExtent']|n}];
Crdppf.mapOverviewSizeW = "${request.registry.settings['mapOverviewSizeW']}";
Crdppf.mapOverviewSizeH = "${request.registry.settings['mapOverviewSizeH']}";
Crdppf.keymap= "${request.registry.settings['keymap']}";
Crdppf.OLImgPath = "${request.static_url('crdppf:static/images/ol/')}";
