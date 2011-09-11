Redefine Login Page
===================

To redefine the login page, you can copy the apex_template.mako and place
it in your own templates directory and override the existing template with:

**development.ini**

::

    apex.apex_template = project:templates/auth.mako

**Minimal Form (Mako)**

::

    % if form:
    ${form.render()|n}
    % endif

    % if velruse_forms:
        % for provider_form in velruse_forms:
            ${provider_form.render(
                action='/velruse/%s/auth' % provider_form.provider_name,
                submit_text=provider_form.provider_proper_name,
            )|n}
        % endfor
    % endif

If you want to redefine the actual form:

*development.ini*:

::

    apex.register_form_class = project.models.Auth

*project/models/__init__.py*:

::

    from wtforms import PasswordField
    from wtforms import RadioField
    from wtforms import TextField
    from wtforms import validators

    from pyramid.i18n import TranslationString as _

    from apex.forms import LoginForm

    class Auth(LoginForm):
        username = TextField(_('Username'), validators=[validators.Required()])
        password = PasswordField(_('Password'), validators=[validators.Required()])
        otherfield = TextField(_('otherfield'), validators=[validators.Required()])
