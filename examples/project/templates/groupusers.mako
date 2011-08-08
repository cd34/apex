<%namespace file="pyramid_apex:templates/flash_template.mako" import="*"/>
${apex_head()}
${apex_flash()}
<p>
This page is only visible to users in the Group 'users'
</p>
<a href="${request.route_path('home')}">Home</a>
<a href="${request.route_path('pyramid_apex_logout')}">Logout</a>
