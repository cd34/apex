Deform
======

.. autofunction:: apex.ext.deform.deferred_csrf_token

generate the value for the csrf token to be inserted into the form

::

    # define form schema
    from apex.ext.deform import deferred_csrf_token

    class SubmitNewsSchema(MappingSchema):
        csrf_token = colander.SchemaNode(
        colander.String(),
            widget = deform.widget.HiddenWidget(),
            default = deferred_csrf_token,
        )

    # in your view, bind the token to the schema
    schema = SubmitNewsSchema(validator=SubmitNewsValidator).bind(csrf_token=request.session.get_csrf_token())


NOTE: colander overwrites the docstring due to the decorator
functools.WRAPPER_ASSIGNMENTS should fix colander, but, not entirely sure
whether that is the correct fix.
