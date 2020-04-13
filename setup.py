#!/usr/bin/env python
"""The setup script."""

from setuptools import setup, find_packages
from requirements import *

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

setup(
    author="Storm Development Ltda",
    author_email='playerstars@stormsec.com.br',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: Portuguese',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    description="Componentes de adapters do Playerstars para GraphQL",
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='playerstars_adapters',
    name='playerstars_adapters',
    packages=find_packages(include=['playerstars_adapters']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://gitlab.com/stormsecurity/internos/playerstars/'
        'playerstars-graphql-adapters.git',
    version='0.1.0',
    zip_safe=False,
)
