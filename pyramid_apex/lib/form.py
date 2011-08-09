import cgi

from wtforms import Form
from wtforms import validators

from pyramid.renderers import render

#http://groups.google.com/group/wtforms/msg/d6e5aca36a69ff5d
class ExtendedForm(Form):    
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

        return render('pyramid_apex:templates/forms/tableform.mako', {
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
