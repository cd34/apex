<%def name="apex_head()">
<link rel="stylesheet" href="${request.static_url('apex:static/css/apex_flash.css')}" type="text/css" media="screen" charset="utf-8" />
</%def>

<%def name="apex_flash()">
% for flashmsg in flash.get_all():
    <div class="flash">
        <p class="${flashmsg['queue']}">${flashmsg['message']}</p>
    </div>
% endfor
</%def>
