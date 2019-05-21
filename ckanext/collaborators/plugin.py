import logging

import ckan.plugins as p
import ckan.plugins.toolkit as toolkit

from ckanext.collaborators.model import tables_exist
from ckanext.collaborators.logic import action, auth

log = logging.getLogger(__name__)


class CollaboratorsPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)

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

    # IActions
    def get_actions(self):
        return {
            'dataset_collaborator_create': action.dataset_collaborator_create,
            'dataset_collaborator_delete': action.dataset_collaborator_delete,
        }

    # IAuthFunctions
    def get_auth_functions(self):
        return {
            'dataset_collaborator_create': auth.dataset_collaborator_create,
            'dataset_collaborator_delete': auth.dataset_collaborator_delete,
        }
