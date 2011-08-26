Routes
======

Routes installed in your application that can be called within your templates
or views

::

    Route Name: apex_login - /auth/login
    Route Name: apex_logout - /auth/logout
    Route Name: apex_register - /auth/register
    Route Name: apex_password - /auth/password
    Route Name: apex_forgot - /auth/forgot
    Route Name: apex_reset - /auth/reset
    Route Name: apex_callback - /auth/callback

The routes can be overridden by changing route_prefix in the line added in 
**__init__.py**:

::

    config.include('apex', route_prefix='/auth')

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
