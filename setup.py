#!/usr/bin/env python3

from setuptools import setup 

with open('README.rst') as f:
	long_description = f.read()
	
setup(name='gridaurora',
      version='0.1',
	  description='utilities for ionospheric gridding, particularly for the aurora',
	  long_description=long_description,
	  author='Michael Hirsch',
	  author_email='hirsch617@gmail.com',
	  url='https://github.com/scienceopen/gridaurora',
	  install_requires=['pandas','six','pytz','numpy','scipy','h5py'],
      packages=['gridaurora'],
	  )

