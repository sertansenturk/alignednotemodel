#!/usr/bin/env python

from setuptools import setup

setup(name='aligned-note-models',
      version='1.0',
      author='Sertan Senturk',
      author_email='contact AT sertansenturk DOT com',
      license='agpl 3.0',
      description='Tools to compute models for notes from audio-score alignment results',
      url='http://sertansenturk.com',
      packages=['alignednotemodel'],
      install_requires=[
          "numpy",
          "matplotlib"
      ],
)

