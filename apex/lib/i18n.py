class Translator(object):
    def __init__(self, localizer):
        self.t = localizer
    def gettext(self, string):
        return self.t.translate(string)
    def ngettext(self, single, plural, string):
        return self.t.pluralize(single, plural, string)
