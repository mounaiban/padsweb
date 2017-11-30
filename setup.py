#
#
# Public Archive of Days Since Timers
# Setuptools Configuration
#
#

import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(
	os.path.abspath(__file__), os.pardir)))

setup(
    name='django-padsweb',
    version='0.5832',
    packages=find_packages(),
    include_package_data=True,
    description='''Yet another long-term stopwatch web app. Works just 
    like the countless "days since" personal calendar apps found on
     Google Play and the App Store, but intended to be accessible 
     from about any reasonably modern device with a web browser and 
     an internet connection.''',
    long_description=README,
    url='https://github.com/mounaiban/padsweb',
    author='Mounaiban',
    author_email='whatever@mounaiban.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Operating System Independent',
        'Programming Language :: Python :: 3.6',
		],
)
