import logging

import ckan.plugins as p
from ckan.lib.plugins import DefaultPermissionLabels
import ckan.plugins.toolkit as toolkit

from ckanext.collaborators.model import tables_exist
from ckanext.collaborators.logic import action, auth

log = logging.getLogger(__name__)


class CollaboratorsPlugin(p.SingletonPlugin, DefaultPermissionLabels):
    p.implements(p.IConfigurer)
    p.implements(p.IActions)
    p.implements(p.IAuthFunctions)
    p.implements(p.IPermissionLabels)

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
            'dataset_collaborator_list': action.dataset_collaborator_list,
            'dataset_collaborator_list_for_user': action.dataset_collaborator_list_for_user,
        }

    # IAuthFunctions

    def get_auth_functions(self):
        return {
            'dataset_collaborator_create': auth.dataset_collaborator_create,
            'dataset_collaborator_delete': auth.dataset_collaborator_delete,
            'dataset_collaborator_list': auth.dataset_collaborator_list,
            'dataset_collaborator_list_for_user': auth.dataset_collaborator_list_for_user,
            'package_update': auth.package_update,
        }

    # IPermissionLabels

    def get_dataset_labels(self, dataset_obj):

        labels = super(CollaboratorsPlugin, self).get_dataset_labels(dataset_obj)

        # Add a generic label for all this dataset collaborators
        labels.append(u'collaborator-{}'.format(dataset_obj.id))

        return labels

    def get_user_dataset_labels(self, user_obj):

        labels = super(CollaboratorsPlugin, self).get_user_dataset_labels(user_obj)

        if not user_obj:
            return labels

        # Add a label for each dataset this user is a collaborator of
        datasets = toolkit.get_action('dataset_collaborator_list_for_user')(
                {'ignore_auth': True}, {'id': user_obj.id})

        for dataset in datasets:
            labels.append('collaborator-{}'.format(dataset['dataset_id']))

        return labels
