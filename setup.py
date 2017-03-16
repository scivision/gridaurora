#!/usr/bin/env python
from setuptools import setup

req = ['python-dateutil','pytz','nose','numpy','scipy','xarray','h5py','astropy','matplotlib','seaborn',
      'sciencedates',
        'pathvalidate']


setup(name='gridaurora',
      packages=['gridaurora'],
      author='Michael Hirsch, Ph.D.',
      description='Gridding for auroral and ionospheric modeling',
      url='https://github.com/scivision/gridaurora',
      version='0.5',
      data_files=[('gridaurora/data',['gridaurora/data/RecentIndices.txt'])],
	  install_requires=req,
      extras_require={'lowtran':'lowtran'}, #optional
      dependency_links = [
      'https://github.com/scivision/lowtran/tarball/master#egg=lowtran',],
      package_data={'gridaurora.precompute': ['*.h5']},
	  )

