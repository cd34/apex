from setuptools import setup, find_packages

version = '0.9.0'

setup(
    version = version,
    name = 'Apex',
    long_description = 'Pyramid starter project to add Velruse, Flash Messages, CSRF, ReCaptcha and Sessions',
    install_requires=[
      "cryptacular",
      "velruse",
      "pyramid",
      "pyramid_mailer",
      "wtforms",
      "wtforms-recaptcha",
    ],
    packages= find_packages(),
    include_package_data=True,
    zip_safe=True,
)
