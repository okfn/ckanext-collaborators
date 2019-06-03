from ckan.plugins import toolkit

from ckan.logic.auth import get_package_object
from ckan.authz import has_user_permission_for_group_or_org
from ckan.logic.auth.update import package_update as core_package_update


def _auth_collaborator(context, data_dict, message):
    user = context['user']

    dataset = toolkit.get_action('package_show')(
        {'ignore_auth': True}, {'id': data_dict['id']})

    owner_org = dataset.get('owner_org')
    if not owner_org:
        return {'success': False}

    if not has_user_permission_for_group_or_org(
            owner_org, user, 'membership'):
        return {
            'success': False,
            'msg': toolkit._(message) % user}

    return {'success': True}


def dataset_collaborator_create(context, data_dict):
    '''Checks if a user is allowed to add collaborators to a dataset

    The current implementation restricts this ability to Administrators of the
    organization the dataset belongs to.
    '''
    return _auth_collaborator(context, data_dict,
        'User %s not authorized to add members to this dataset')


def dataset_collaborator_delete(context, data_dict):
    '''Checks if a user is allowed to delete collaborators from a dataset

    The current implementation restricts this ability to Administrators of the
    organization the dataset belongs to.
    '''
    return _auth_collaborator(context, data_dict,
        'User %s not authorized to remove members from this dataset')


def dataset_collaborator_list(context, data_dict):
    '''Checks if a user is allowed to list collaborators from a dataset

    The current implementation restricts this ability to Administrators of the
    organization the dataset belongs to.
    '''
    return _auth_collaborator(context, data_dict,
        'User %s not authorized to list members from this dataset')


def dataset_collaborator_list_for_user(context, data_dict):
    '''Checks if a user is allowed to list all datasets a user is acollaborator in

    The current implementation restricts to the own users themselves.
    '''
    user_obj = context.get('auth_user_obj')
    if user_obj and data_dict.get('id') in (user_obj.name, user_obj.id):
        return {'success': True}
    return {'success': False}


# Core overrides
# TODO: remove the direct core import and use the chained_auth_function
# decorator once #4248 et al are backported into 2.8
def package_update(context, data_dict):

    result = core_package_update(context, data_dict)

    if result['success']:
        return result

    user_name = context['user']
    dataset = get_package_object(context, data_dict)

    datasets = toolkit.get_action(
        'dataset_collaborator_list_for_user')(
            context, {'id': user_name, 'capacity': 'editor'})
    return {
        'success': dataset.id in [d['dataset_id'] for d in datasets]}
