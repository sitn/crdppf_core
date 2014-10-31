<%inherit file="../base/index.mako"/>


% if debug:
    <!-- GENERAL LIBRARIES -->
    
    <!-- CUSTOM CRDPPF STUFF -->
    <!-- extensions -->
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/menu/RangeMenu.js')}" type="text/javascript"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/menu/ListMenu.js')}" type="text/javascript"></script>

    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/adminPanel.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/adminToolbar.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/translationsPanel.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/GridFilters.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/filter/Filter.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/filter/StringFilter.js')}" type="text/javascript"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/filter/DateFilter.js')}" type="text/javascript"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/filter/ListFilter.js')}" type="text/javascript"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/filter/NumericFilter.js')}" type="text/javascript"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/filter/BooleanFilter.js')}" type="text/javascript"></script>
% else:
   <!-- extensions -->
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/menu/RangeMenu.js')}" type="text/javascript"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/menu/ListMenu.js')}" type="text/javascript"></script>

    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/adminPanel.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/adminToolbar.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/translationsPanel.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/GridFilters.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/filter/Filter.js')}"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/filter/StringFilter.js')}" type="text/javascript"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/filter/DateFilter.js')}" type="text/javascript"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/filter/ListFilter.js')}" type="text/javascript"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/filter/NumericFilter.js')}" type="text/javascript"></script>
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/resources/ux/gridfilters/filter/BooleanFilter.js')}" type="text/javascript"></script>
% endif
    
<div id="main"></div>
