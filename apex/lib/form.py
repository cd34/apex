import cgi

from wtforms import Form
from wtforms import validators

from pyramid.i18n import get_localizer
from pyramid.renderers import render
from pyramid.threadlocal import get_current_request

from apex.lib.db import merge_session_with_post
from apex.lib.i18n import Translator

class ExtendedForm(Form):
    """ Base Model used to wrap WTForms for local use
    Global Validator, Renderer Function, determines whether
    it needs to be multipart based on file field present in form.

    http://groups.google.com/group/wtforms/msg/d6e5aca36a69ff5d
    """

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        self.request = kwargs.pop('request', get_current_request())
        super(Form, self).__init__(self._unbound_fields, prefix=prefix)

        self.is_multipart = False

        for name, field in self._fields.iteritems():
            if field.type == 'FileField':
                self.is_multipart = True

            setattr(self, name, field)

        self.process(formdata, obj, **kwargs)

    def hidden_fields(self):
        """ Returns all the hidden fields.
        """
        return [self._fields[name] for name, field in self._unbound_fields
            if self._fields.has_key(name) and self._fields[name].type == 'HiddenField']

    def visible_fields(self):
        """ Returns all the visible fields.
        """
        return [self._fields[name] for name, field in self._unbound_fields
            if self._fields.has_key(name) and not self._fields[name].type == 'HiddenField']

    def _get_translations(self): 
        if self.request:
            localizer = get_localizer(self.request)
            return Translator(localizer)

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
        template = kwargs.pop('template', False)

        if not template:
            settings = self.request.registry.settings

            template = settings.get('apex.form_template', \
                'apex:templates/forms/tableform.mako')

        return render(template, {
            'form': self,
            'action': action,
            'submit_text': submit_text,
            'args': kwargs,
        }, request=self.request)

class StyledWidget(object): 
    """ Allows a user to pass style to specific form field

    http://groups.google.com/group/wtforms/msg/6c7dd4dc7fee872d
    """
    def __init__(self, widget=None, **kwargs): 
        self.widget = widget
        self.kw = kwargs

    def __call__(self, field, **kwargs):
        if not self.widget:
            self.widget = field.__class__.widget

        return self.widget(field, **dict(self.kw, **kwargs)) 

class FileRequired(validators.Required): 
    """ 
    Required validator for file upload fields. 

    Bug mention for validating file field:
    http://groups.google.com/group/wtforms/msg/666254426eff1102
    """ 
    def __call__(self, form, field): 
        if not isinstance(field.data, cgi.FieldStorage): 
            if self.message is None: 
                self.message = field.gettext(u'This field is required.') 
            field.errors[:] = [] 
            raise validators.StopValidation(self.message)

class ModelForm(ExtendedForm):
    """ Simple form that adds a save method to forms for saving 
        forms that use WTForms' model_form function.
    """
    def save(self, session, model, commit=True):
        record = model()
        record = merge_session_with_post(record, self.data.items())
        if commit:
            session.add(record)
            session.flush()

        return record
