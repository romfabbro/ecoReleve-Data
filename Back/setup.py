import os
import sys
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = [
    ]

setup(name='ecoreleve_server',
      version='1.0',
      description='ecoReleve_Server',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='ecoreleve_server',
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = ecoreleve_server:main
      [console_scripts]
      initialize_ecoReleve_Server_db = ecoreleve_server.scripts.initializedb:main
      """,
      )
