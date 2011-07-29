<%namespace file="pyramid_apex:templates/flash_template.mako" import="*"/>
${apex_head()}
${apex_flash()}
<p>
This is the sample index page
</p>
<a href="${request.route_path('protected')}">Protected Page</a>
<a href="${request.route_path('pyramid_apex_logout')}">Logout</a>
