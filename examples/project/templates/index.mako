<%namespace file="apex:templates/flash_template.mako" import="*"/>
${apex_head()}
${apex_flash()}
<p>
This is the sample index page
</p>
<a href="${request.route_path('protected')}">Protected Page</a><br/>
<a href="${request.route_path('groupusers')}">Page Restricted to users in group 'users'</a> - by default, no users are placed in users<br/>
<a href="${request.route_path('apex_logout')}">Logout</a><br/>
