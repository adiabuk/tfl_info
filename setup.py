#!/usr/bin/env python

"""
Setup script for tfl_info
"""

from setuptools import setup

with open('requirements.txt', 'r') as reqs_file:
    REQS = reqs_file.readlines()
VER = '0.1'

setup(
    name='tflinfo',
    packages=['tflinfo'],
    version=VER,
    description='bike scripts',
    author='Amro Diab',
    author_email='adiab@linuxmail.org',
    url='https://github.com/adiabuk/tfl_info',
    keywords=['tfl', 'bikes'],
    install_requires=REQS,
    entry_points={'console_scripts':['londonbikes=tflinfo.tfl:main']},
    test_suite='',
    classifiers=[],
)
