if(!window.Crdppf) Crdppf = {};

<%
    counter = 1
    total = len(fr)
%>
    
Crdppf.labels = {
    % for key in fr:
       '${key}' : '${fr[key]}'
        % if counter < total:
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
        '${layer}'
        % if j < nblayers:
            ,
        %endif
        <%
            j += 1
        %>
    % endfor
];