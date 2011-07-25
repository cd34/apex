<h1>${title}</h1>

<form action="" method="POST" accept-charset="utf-8">
	<%include file="form.mako"/>
	<input type="submit" name="submit" value="Submit" />
</form>

<form action="/velruse/facebook/auth" method="post">
${csrf_token_field|n}
<input type="hidden" name="end_point" value="${request.route_url('pyramid_apex_callback')}?csrf_token=${csrf_token}" />
<input type="submit" value="Login with Facebook" />
</form>

<form action="/velruse/google/auth" method="post">
${csrf_token_field|n}
<input type="hidden" name="popup_mode" value="popup" />
<input type="hidden" name="end_point" value="${request.route_url('pyramid_apex_callback')}?csrf_token=${csrf_token}" />
<input type="submit" value="Login with Google" />
</form>

<form action="/velruse/openid/auth" method="post">
${csrf_token_field|n}
<input type="hidden" name="end_point" value="${request.route_url('pyramid_apex_callback')}?csrf_token=${csrf_token}" />
<input type="text" name="openid_identifier" value="https://www.google.com/accounts/o8/id" size="80"/>
<input type="submit" value="Login with OpenID" />
</form>

<form action="/velruse/yahoo/auth" method="post">
${csrf_token_field|n}
<input type="hidden" name="end_point" value="${request.route_url('pyramid_apex_callback')}?csrf_token=${csrf_token}" />
<input type="hidden" name="oauth" value="true" />
<input type="submit" value="Login with Yahoo" />
</form>

<form action="/velruse/twitter/auth" method="post">
${csrf_token_field|n}
<input type="hidden" name="end_point" value="${request.route_url('pyramid_apex_callback')}?csrf_token=${csrf_token}" />
<input type="submit" value="Login with Twitter" />
</form>

<a href="${request.route_path('pyramid_apex_forgot')}">Forgot my Password</a>
