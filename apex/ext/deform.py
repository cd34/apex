import colander

@colander.deferred
def deferred_csrf_token(node, kw):
    """
    generate the value for the csrf token to be inserted into the form

    .. codeblock:: python

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

    """
    csrf_token = kw.get('csrf_token')
    return csrf_token
