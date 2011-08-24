Redefine Login Page
===================

To redefine the login page, you can copy the apex_template.mako and place
it in your own templates directory and override the existing template with:

**development.ini**

::

    apex.apex_template = project:templates/auth.mako

**Minimal Form (Mako)**

::

    ${form.render()|n}

    %if velruse_forms:
        %for provider_form in velruse_forms:
            ${provider_form.render(
                action='/velruse/%s/auth' % provider_form.provider_name,
                submit_text=provider_form.provider_proper_name,
            )|n}
        %endfor
    %endif
