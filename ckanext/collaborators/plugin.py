import logging

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

from ckanext.collaborators.model import tables_exist

log = logging.getLogger(__name__)


class CollaboratorsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        if not tables_exist():
            log.critical(u'''
The dataset collaborators extension requires a database setup. Please run the following
to create the database tables:
    paster --plugin=ckanext-collaborators collaborators init-db
''')
        else:
            log.debug(u'Dataset collaborators tables exist')

        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'collaborators')
