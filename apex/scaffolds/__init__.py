from paste.util.template import paste_script_template_renderer
from pyramid.scaffolds import PyramidTemplate

class ApexRoutesAlchemyTemplate(PyramidTemplate):
    _template_dir = 'apex_routesalchemy'
    summary = 'Pyramid SQLAlchemy project using url dispatch, and apex'
    template_renderer = staticmethod(paste_script_template_renderer)