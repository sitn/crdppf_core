# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='crdppf',
    version='3.1.4',
    description='SITN, public law restriction portal core',
    author='sitn',
    author_email='sitn@ne.ch',
    url='http://www.ne.ch/sitn',
    install_requires=[
        'c2c.template',
        'dogpile.cache',
        'httplib2',
        'jstools',
        'papyrus',
        'pyramid_tm',
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            "iconizer = crdppf.utilities.iconizer:main",
        ],
        'paste.app_factory': [
            'main = crdppf_core:main',
        ],
    },
)
