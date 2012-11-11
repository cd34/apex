<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
<title>Apex</title>
<%namespace file="apex:templates/flash_template.mako" import="*"/>

<link rel="stylesheet" href="${request.static_url('apex:static/css/apex_forms.css')}" type="text/css" media="screen" charset="utf-8" />
${apex_head()}
<style type="text/css">
body { margin: 10px auto 10px auto; width: 400px; font-family: Verdana, sans;}
</style>
</head>
<body>
${apex_flash()}

<h1>${title}</h1>

% if form:
${form.render()|n}
% endif

% if velruse_forms:
	% for provider_form in velruse_forms:
		${provider_form.render(
			action='/velruse/login/%s' % provider_form.provider_name,
			submit_text=provider_form.provider_proper_name,
		)|n}
	% endfor
% endif

% if action != 'login':
<a href="${request.route_path('apex_login')}">Login</a>
% endif
% if action != 'register':
<a href="${request.route_path('apex_register')}">Create an Account</a>
% endif
% if action != 'forgot':
<a href="${request.route_path('apex_forgot')}">Forgot my Password</a>
% endif
</body>
</html>
