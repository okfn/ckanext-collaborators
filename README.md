# ckanext-collaborators

[![Build Status](https://travis-ci.org/okfn/ckanext-collaborators.svg?branch=master)](https://travis-ci.org/okfn/ckanext-collaborators)

This extension adds the ability to assign roles on individual datasets to individual users, alongside the standard organization-based ones.

## Installation

To install ckanext-collaborators, activate your CKAN virtualenv and run:

    git clone https://github.com/okfn/ckanext-collaborators.git
    cd ckanext-collaborators
    python setup.py develop

Create the database tables running:

    paster collaborators init-db -c ../path/to/ini/file


## Configuration

Once installed, add the `collaborators` plugin to the `ckan.plugins` configuration option on your INI file:

    ckan.plugins = ... collaborators

