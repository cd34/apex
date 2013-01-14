import os

from setuptools import find_packages
from setuptools import setup

version = '0.9.7'

install_requires = [
    "cryptacular",
    "zope.sqlalchemy",
    "velruse>=1.0.3",
    "pyramid>1.1.2",
    "pyramid_mailer",
    "requests",
    "wtforms",
    "wtforms-recaptcha",
]

tests_require = install_requires + ['Sphinx', 'docutils',
                                    'WebTest', 'virtualenv', 'nose']

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

kwargs = dict(
    version=version,
    name='apex',
    description="""\
Pyramid toolkit to add Velruse, Flash Messages,\
CSRF, ReCaptcha and Sessions""",
    long_description=README + '\n\n' + CHANGES,
    classifiers=[
      "Intended Audience :: Developers",
      "Programming Language :: Python",
      "License :: OSI Approved :: MIT License",
    ],
    install_requires=install_requires,
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,
    tests_require=tests_require,
    test_suite="apex.tests",
    url="http://thesoftwarestudio.com/apex/",
    author="Chris Davies",
    author_email='user@domain.com',
    entry_points="""\
        [paste.paster_create_template]
        apex_routesalchemy=apex.scaffolds:ApexRoutesAlchemyTemplate
    """
)

# to update catalogs, use babel and lingua !
try:
    import babel
    babel = babel  # PyFlakes
    # if babel is installed, advertise message extractors (if we pass
    # this to setup() unconditionally, and babel isn't installed,
    # distutils warns pointlessly)
    kwargs['message_extractors'] = {".": [
        ("**.py",     "lingua_python", None),
        ('**.mako', 'mako', None),
        ("**.pt", "lingua_xml", None), ]
    }
except ImportError:
    pass

setup(**kwargs)
