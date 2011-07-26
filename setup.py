from setuptools import setup, find_packages

version = '0.9.0'

setup(
    version = version
    name = 'Pyramid Apex',
    long_description = 'Pyramid starter project to add Velruse, Flash Messages, CSRF, ReCaptcha and Sessions',
    version= version,
    install_requires=[
      "py-bcrypt",
      "velruse",
      "pyramid",
      "wtforms",
      "wtforms-recaptcha",
    ],
    packages= find_packages(),
)
