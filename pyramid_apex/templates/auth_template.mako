<h1>${title}</h1>

<form action="" method="POST" accept-charset="utf-8">
	<%include file="form.mako"/>
	<input type="submit" name="submit" value="Submit" />
</form>

<a href="${request.route_path('pyramid_apex_forgot')}">Forgot my Password</a>
