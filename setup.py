from setuptools import setup, find_packages
import sys, os

version = '0.1'

setup(name='CabochonServer',
      version=version,
      description="Cabochon server helper library",
      long_description="""\
""",
      classifiers=[], # Get strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      keywords='',
      author='David Turner',
      author_email='novalis@openplans.org',
      url='http://www.openplans.org/projects/cabochon',
      license='GPLv2 or any later version',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
        "WSSEAuth",
        "decorator",
        "paste"
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
