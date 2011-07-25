<link rel="stylesheet" href="${request.static_url('pyramid_apex:static/css/apex_forms.css')}" type="text/css" media="screen" charset="utf-8" />

<h1>${title}</h1>

${form.render()|n}

%for provider_form in velruse_forms:
	${provider_form.render(
		action='/velruse/%s/auth' % provider_form.provider_name,
		submit_text=provider_form.provider_name,
	)|n}
%endfor

<a href="${request.route_path('pyramid_apex_forgot')}">Forgot my Password</a>
