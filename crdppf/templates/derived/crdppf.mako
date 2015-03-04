<%inherit file="../base/index.mako"/>

% if debug:
    <%!
    from jstools.merge import Merger
    %>
    <%
    jsbuild_cfg = request.registry.settings.get('jsbuild_cfg')
    jsbuild_root_dir = request.registry.settings.get('jsbuild_root_dir')
    %>

    % for script in Merger.from_fn(jsbuild_cfg.split(), root_dir=jsbuild_root_dir).list_run(['crdppf.js']):
    <script type="text/javascript" src="${request.static_url(script.replace('crdppf_core/crdppf/', 'crdppf:', 1))}"></script>
    <!--${script}-->
    %endfor

% else:
    <script type="text/javascript" src="${request.static_url('crdppf:static/build/crdppf.js')}"></script>
% endif

    <script type="text/javascript">
% if plan_cadastral:
    Crdppf.defaultTiles['wmtsname'] = "${plan_cadastral['tile_date']}";
    Crdppf.defaultTiles['tile_format'] = "${plan_cadastral['tile_format']}";
% endif
        OpenLayers.Util.extend(OpenLayers.Lang.fr, {
% if plan_ville:
            '${plan_ville}': 'Plan de ville',
% endif
% if plan_cadastral:
            '${plan_cadastral}': 'Plan cadastral'
% endif
        });
    </script>
    
<div id="main"></div>
