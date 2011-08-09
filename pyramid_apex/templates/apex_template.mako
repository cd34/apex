<link rel="stylesheet" href="${request.static_url('pyramid_apex:static/css/apex_forms.css')}" type="text/css" media="screen" charset="utf-8" />
<link rel="stylesheet" href="${request.static_url('pyramid_apex:static/css/apex_flash.css')}" type="text/css" media="screen" charset="utf-8" />

% for flashmsg in flash.get_all():
    <div class="flash">
        <p class="${flashmsg['queue']}">${flashmsg['message']}</p>
    </div>
% endfor

<h1>${title}</h1>

${form.render()|n}

%if velruse_forms:
	%for provider_form in velruse_forms:
		${provider_form.render(
			action='/velruse/%s/auth' % provider_form.provider_name,
			submit_text=provider_form.provider_name,
		)|n}
	%endfor
%endif

<a href="${request.route_path('pyramid_apex_forgot')}">Forgot my Password</a>
<a href="${request.route_path('pyramid_apex_register')}">Create an Account</a>
