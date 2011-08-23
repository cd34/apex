Routes
======

Routes installed in your application that can be called within your templates
or views

::

    Route Name: apex_login - /apex/login
    Route Name: apex_logout - /apex/logout
    Route Name: apex_register - /apex/register
    Route Name: apex_password - /apex/password
    Route Name: apex_forgot - /apex/forgot
    Route Name: apex_reset - /apex/reset
    Route Name: apex_callback - /apex/callback

In your mako templates, these can be accessed as:

::

    <a href="${request.route_url('apex_login')}">Login</a>
    <a href="${request.route_url('apex_logout')}">Logout</a>
    <a href="${request.route_url('apex_register')}">Register</a>
    <a href="${request.route_url('apex_password')}">Change Password</a>
    <a href="${request.route_url('apex_forgot')}">Forgot Password</a>
    <a href="${request.route_url('apex_reset')}">Reset Password</a>
    <a href="${request.route_url('apex_callback')}">Apex Callback</a>

In your jinja2 templates, these can be accessed as:

::

    <a href="{{request.route_url('apex_login')}}">Login</a>
    <a href="{{request.route_url('apex_logout')}}">Logout</a>
    <a href="{{request.route_url('apex_register')}}">Register</a>
    <a href="{{request.route_url('apex_password')}}">Change Password</a>
    <a href="{{request.route_url('apex_forgot')}}">Forgot Password</a>
    <a href="{{request.route_url('apex_reset')}}">Reset Password</a>
    <a href="{{request.route_url('apex_callback')}}">Apex Callback</a>
