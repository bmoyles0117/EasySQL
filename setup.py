#!/usr/bin/env python

from setuptools import setup
import os

def generate_data_files(*dirs):
    results = []

    for src_dir in dirs:
        for root,dirs,files in os.walk(src_dir):
            results.append((root, map(lambda f:root + "/" + f, files)))
    return results

setup(
    name='Easy SQL',
    version='0.005',
    description='An object oriented way of building SQL queries using python',
    author='Bryan Moyles',
    author_email='bryan.moyles@teltechcorp.com',
    url='http://www.bryanmoyles.com/',
    packages=['easysql']
)
