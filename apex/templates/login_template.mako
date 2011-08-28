% if action != 'login':
<a href="${request.route_path('apex_login')}">Login</a>
% endif
% if action != 'register':
<a href="${request.route_path('apex_register')}">Create an Account</a>
% endif
% if action != 'forgot':
<a href="${request.route_path('apex_forgot')}">Forgot my Password</a>
% endif
