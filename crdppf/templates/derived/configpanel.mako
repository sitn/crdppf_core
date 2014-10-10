<%inherit file="../base/index.mako"/>


% if debug:
    <!-- GENERAL LIBRARIES -->
    
    <!-- CUSTOM CRDPPF STUFF -->
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/adminPanel.js')}"></script>
% else:
    <script type="text/javascript" src="${request.static_url('crdppf:static/js/Crdppf/adminPanel.js')}"></script>
% endif
    
<div id="main"></div>
