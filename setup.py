#!/usr/bin/env python

from os.path import abspath, dirname, join
from setuptools import setup, find_packages
import glob
ROOT = dirname(abspath(__file__))

version_file = join(ROOT, 'PerfectoLibrary', 'version.py')
exec (compile(open(version_file).read(), version_file, 'exec'))

setup(name='perfectolibrary-py3',
      version=VERSION,
      description='Robot Framework Mobile app testing library for using Perfecto Cloud',
      author='Jack Deng',
      author_email='jdeng@perforce.com',
      url='https://github.com/PerfectoMobileSA/Robotframework-PerfectoLibrary',
      license='MIT License',
      keywords='robotframework testing Perfecto mobile appium webdriver app android ios',
      platforms='any',
      data_files=glob.glob('PerfectoLibrary/listeners/data/**'),
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Software Development :: Testing",
          'Programming Language :: Python',
          'Programming Language :: Python :: 3'
      ],
      install_requires=[
          'decorator >= 3.3.2',
          'robotframework >= 6.0',
          'docutils >= 0.8.1',
          'Appium-Python-Client >= 2.0.0',
          'selenium >= 2.47.1',
          'robotframework-appiumlibrary >= 1.6.4',
          'robotframework-seleniumlibrary >= 6.1.0',
          'robotframework-selenium2library >= 3.0.0',
          'Selenium2LibraryExtension >= 1.1.0',
          'perfecto-py3-ps >= 1.0.4',
          'six >= 1.11.0',
          'axe-core-python >= 0.1.0'
      ],
      packages=find_packages(exclude=["demo", "docs", "tests", ]),
      include_package_data=True,
      )
