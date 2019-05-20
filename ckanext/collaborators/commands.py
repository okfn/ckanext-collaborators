# encoding: utf-8

import sys
import logging

from ckan.plugins.toolkit import CkanCommand

from ckanext.collaborators.model import tables_exist, create_tables


class DatasetCollaborators(CkanCommand):
    u'''Utilities for the CKAN dataset collaborators extension

    Usage:
        paster collaborators init-db
            Initialize database tables

    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    max_args = 9
    min_args = 0

    def __init__(self, name):

        super(DatasetCollaborators, self).__init__(name)

    def command(self):
        self._load_config()

        if len(self.args) != 1:
            self.parser.print_usage()
            sys.exit(1)

        cmd = self.args[0]
        if cmd == 'init-db':
            self.init_db()
        else:
            self.parser.print_usage()
            sys.exit(1)

    def init_db(self):

        if tables_exist():
            print(u'Dataset collaborators tables already exist')
            sys.exit(1)

        create_tables()

        print(u'Dataset collaborators tables created')
