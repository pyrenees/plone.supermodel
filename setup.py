# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup
import os
import sys


# if <= Python 2.6 or less, specify minimum zope.schema compatible:
ZOPESCHEMA = 'zope.schema'
if sys.version_info < (2, 7):
    ZOPESCHEMA += '>=4.1.0'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

version = '1.2.8.dev0'

long_description = (
    read('README.rst')
    + '\n' +
    read('CHANGES.rst')
    + '\n'
    )

setup(
    name='plone.supermodel',
    version=version,
    description="Serialize Zope schema definitions to and from XML",
    long_description=long_description,
    # Get more strings from
    # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: BSD License",
    ],
    keywords='Plone XML schema',
    author='Martin Aspeli',
    author_email='optilude@gmail.com',
    url='https://github.com/plone/plone.supermodel',
    license='BSD',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'lxml',
        'zope.component',
        'zope.i18nmessageid',
        'zope.interface',
        ZOPESCHEMA,
        'zope.deferredimport',
        'zope.dottedname',
        'z3c.zcmlhook',
        'six',
    ],
    extras_require={
        'lxml': [],  # BBB
        'plone.rfc822': ['plone.rfc822'],
        'test': [
            'plone.rfc822',
            ],
    },
    entry_points="""
    # -*- Entry points: -*-
    """,
    )
