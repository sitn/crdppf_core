## -*- coding: utf-8 -*-

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
    <meta charset="UTF-8" /> 
    <meta http-equiv="Content-Type" content="text/html; charset=utf8" />
    <meta http-equiv="X-UA-Compatible" content="IE=edge" />
    <title>Cadastre des restrictions de droit public à la propriété foncière</title>
    <link href="${request.static_url('crdppfportal:static/images/favico.ico')}" rel="shortcut icon" type="image/x-icon" />
    <link rel="stylesheet" href="${request.static_url('crdppf:static/lib/ext/resources/css/ext-all.css')}" type="text/css" media="screen" charset="utf-8" />
    <link rel="stylesheet" href="${request.static_url('crdppf:static/lib/ext/resources/css/xtheme-gray.css')}" type="text/css" media="screen" charset="utf-8" />
    <link rel="stylesheet" href="${request.static_url('crdppf:static/css/main.css')}" type="text/css" media="screen" charset="utf-8" />
    <link rel="stylesheet" href="${request.static_url('crdppf:static/lib/openlayers.addins/theme/default/scalebar-thin.css')}" type="text/css" media="screen" charset="utf-8" />
    <link rel="stylesheet" href="${request.static_url('crdppf:static/css/banner.css')}" type="text/css" media="screen" charset="utf-8" />
    <link rel="stylesheet" href="${request.static_url('crdppf:static/lib/ext/resources/ux/gridfilters/css/GridFilters.css')}" type="text/css" media="screen" charset="utf-8" />
    <link rel="stylesheet" href="${request.static_url('crdppf:static/lib/ext/resources/ux/gridfilters/css/RangeMenu.css')}" type="text/css" media="screen" charset="utf-8" />
    <link rel="stylesheet" href="${request.static_url('crdppf:static/lib/openlayers/theme/default/style.css')}" type="text/css" charset="utf-8" />
    ${self.js()}

    <!-- Load globals -->
    <script type="text/javascript" src="${request.route_url('initjs')}" charset="UTF-8"></script>
    <script type="text/javascript" src="${request.route_url('globalsjs')}" charset="UTF-8"></script>
    

</head>

 
<body>
<%include file='crdppfportal:templates/header.mako'/>
    
% if debug:
    <p>debug:ok</p>
% endif
    ${next.body()}

</body>
</html>


<%def name="js()">
    <script src="${request.static_url('crdppf:static/lib/ext/adapter/ext/ext-base-debug.js')}" type="text/javascript" charset="UTF-8"></script>
    <script src="${request.static_url('crdppf:static/lib/ext/ext-all-debug.js')}" type="text/javascript" charset="UTF-8"></script>

    <!-- <script src="${request.static_url('crdppf:static/lib/ext/adapter/ext/ext-base.js')}" type="text/javascript" charset="UTF-8"></script>-->
    <!-- <script src="${request.static_url('crdppf:static/lib/ext/ext-all.js')}" type="text/javascript" charset="UTF-8"></script> -->

    <script src="${request.static_url('crdppf:static/lib/ext/src/locale/ext-lang-fr.js')}" type="text/javascript" charset="UTF-8"></script>
    
    <!-- <script src="${request.static_url('crdppf:static/lib/ext/resources/ux/statusbar/statusBar.js')}" type="text/javascript" charset="UTF-8"></script> -->
    
</%def>