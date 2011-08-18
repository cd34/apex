import cgi

from wtforms import Form
from wtforms import validators

from pyramid.renderers import render

#http://groups.google.com/group/wtforms/msg/d6e5aca36a69ff5d
class ExtendedForm(Form):

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        super(Form, self).__init__(self._unbound_fields, prefix=prefix)

        self.is_multipart = False

        for name, field in self._fields.iteritems():
            if field.type == 'FileField':
                self.is_multipart = True

            setattr(self, name, field)

        self.process(formdata, obj, **kwargs)

    def clean(self): 
        """Override me to validate a whole form.""" 
        pass

    def validate(self): 
        if not super(ExtendedForm, self).validate(): 
            return False 
        errors = self.clean() 
        if errors: 
            self._errors = {'whole_form': errors} 
            return False 
        return True
        
    def render(self, **kwargs):
        action = kwargs.pop('action', '')
        submit_text = kwargs.pop('submit_text', 'Submit')
        template = kwargs.pop('template', 'tableform')

        return render('apex:templates/forms/%s.mako' % template, {
            'form': self,
            'action': action,
            'submit_text': submit_text,
            'args': kwargs,
        })

#http://groups.google.com/group/wtforms/msg/6c7dd4dc7fee872d
class StyledWidget(object): 
    def __init__(self, widget=None, **kwargs): 
        self.widget = widget
        self.kw = kwargs

    def __call__(self, field, **kwargs):
        if not self.widget:
            self.widget = field.__class__.widget

        return self.widget(field, **dict(self.kw, **kwargs)) 

#http://groups.google.com/group/wtforms/msg/666254426eff1102
class FileRequired(validators.Required): 
    """ 
    Required validator for file upload fields. 
    """ 
    def __call__(self, form, field): 
        if not isinstance(field.data, cgi.FieldStorage): 
            if self.message is None: 
                self.message = field.gettext(u'This field is required.') 
            field.errors[:] = [] 
            raise validators.StopValidation(self.message)
