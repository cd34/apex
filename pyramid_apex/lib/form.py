from wtforms import Form

#http://groups.google.com/group/wtforms/browse_thread/thread/8382c40040b69702
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