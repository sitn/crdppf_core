if(!window.Crdppf) Crdppf = {};

<%
    counter = 1
    total = len(fr)
%>
    
Crdppf.labels = {
    % for key in fr:
       '${key}' : '${fr[key] | n}'
        % if counter < total :
            ,
        %endif
        <%
            counter += 1
        %>
    % endfor
};

<%
    j = 1
    nblayers = len(layerlist)
%>

Crdppf.layers = [
    % for layer in layerlist :
        <%
            i = 1
            nbcols = len(layer)
        %>
            {
            % for key in layer:
                '${key}' : '${layer[key]}'
                % if i < nbcols:
                    ,
                %endif
                <%
                    i += 1
                %>
            % endfor
            }
        % if j < nblayers:
            ,
        %endif
        <%
            j += 1
        %>
    % endfor
];

<%
    j = 1
    nblayers = len(baseLayers)
%>
            
baselayers = [
    % for baselayer in baseLayers :
        <%
            i = 1
            nbcols = len(baselayer)
        %>
            {
            % for key in baselayer:
                '${key}' : '${baselayer[key]}'
                % if i < nbcols:
                    ,
                %endif
                <%
                    i += 1
                %>
            % endfor
            }
        % if j < nblayers:
            ,
        %endif
        <%
            j += 1
        %>
    % endfor
];
Crdppf.baseLayersList = {'baseLayers': baselayers};