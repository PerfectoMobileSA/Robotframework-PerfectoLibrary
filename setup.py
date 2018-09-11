#!/usr/bin/env python

from os.path import abspath, dirname, join
from setuptools import setup, find_packages

ROOT = dirname(abspath(__file__))

version_file = join(ROOT, 'PerfectoLibrary', 'version.py')
exec (compile(open(version_file).read(), version_file, 'exec'))

setup(name='perfectolibrary',
      version=VERSION,
      description='Robot Framework Mobile app testing library for using Perfecto Cloud',
#       long_description=open(join(ROOT, 'README.rst')).read(),
      author='Jack Deng',
      author_email='JackD@perfectoMobile.com',
      url='https://github.com/PerfectoMobileSA/Robotframework-PerfectoLibrary',
      license='Apache License 2.0',
      keywords='robotframework testing Perfecto mobile appium webdriver app android ios',
      platforms='any',
      classifiers=[
          "Development Status :: 3 - Alpha",
          "License :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
          "Topic :: Software Development :: Testing",
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6'
      ],
      setup_requires=[
          "pytest-runner"
      ],
      install_requires=[
          'decorator >= 3.3.2',
          'robotframework >= 2.6.0',
          'docutils >= 0.8.1',
          'Appium-Python-Client >= 0.20',
          'selenium >= 2.47.1',
          'robotframework-appiumlibrary >= 1.3.7',
          'robotframework-seleniumlibrary >= 3.0.0',
          'robotframework-selnium2library >= 1.6.0',
          'Selenium2LibraryExtension >= 1.1.0',
          'perfecto >= 2.0.0.1'
      ],
      packages=find_packages(exclude=["demo", "docs", "tests", ]),
      include_package_data=True,
      )