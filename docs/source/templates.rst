Templates
=========

Mako Template:

To handle flash messages when using Mako, insert the following into your
templates:

::

    <%namespace file="apex:templates/flash_template.mako" import="*"/>
    ${apex_head()}

Insert this line where you would like the Flash Messages to be displayed:

::

    ${apex_flash()}

Jinja Templates:

(Currently not working due to import issue, need to copy 
flash_template.jinja2 to your templates directory)

::

    {# import "apex:templates/flash_template.jinja2" as flash with context-#}
    {% import "flash_template.jinja2" as flash with context -%}

In the <head> section of your template:

::

    {{ flash.apex_head() }}

Insert this line where you would like the Flash Messages to be displayed:

::

    {{ flash.apex_flash() }}
