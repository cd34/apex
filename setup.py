from setuptools import find_packages
from setuptools import setup

version = '0.9.5'

install_requires=[
    "cryptacular",
    "zope.sqlalchemy",
    "velruse==0.20a1dev",
    "pyramid>1.1.2",
    "pyramid_mailer",
    "wtforms",
    "wtforms-recaptcha",
]

tests_require = install_requires + ['Sphinx', 'docutils', 
                                    'WebTest', 'virtualenv', 'nose']

kwargs = dict(
    version=version,
    name='Apex',
    long_description='Pyramid starter project to add Velruse, Flash Messages, CSRF, ReCaptcha and Sessions',
    install_requires=install_requires,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    tests_require=tests_require,
    test_suite="apex.tests",
    entry_points = """\
        [paste.paster_create_template]
        apex_routesalchemy=apex.scaffolds:ApexRoutesAlchemyTemplate
    """ 
)

# to update catalogs, use babel and lingua !
try:
    import babel
    babel = babel # PyFlakes
    # if babel is installed, advertise message extractors (if we pass
    # this to setup() unconditionally, and babel isn't installed,
    # distutils warns pointlessly)
    kwargs['message_extractors'] = { ".": [
        ("**.py",     "lingua_python", None ),
        ('**.mako', 'mako', None),
        ("**.pt", "lingua_xml", None ),
        ]}
except ImportError:
    pass  

setup(**kwargs)
