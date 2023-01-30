import os
from setuptools import setup, find_packages


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(filename):
    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), filename), 'r') as fin:
        return fin.read()


setup(
    name='idnumbers',
    version=read('VERSION').replace('\n', '').replace('\r', ''),
    author='Identique',
    author_email='microdataxyz@outlook.com',
    description='id numbers verification toolkits',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    license='MIT',
    url='https://github.com/Identique/idnumbers',
    project_urls={
        'Source': 'https://github.com/Identique/idnumbers',
        'Tracker': 'https://github.com/Identique/idnumbers/issues',
    },
    packages=find_packages(exclude=['*tests*']),
    data_files=[('version', ['VERSION'])],
    python_requires='>=3.9',
    install_requires=[],
    setup_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'Typing :: Typed'
    ], )
