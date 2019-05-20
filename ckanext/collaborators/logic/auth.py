from ckan.plugins import toolkit
from ckan.authz import has_user_permission_for_group_or_org



def dataset_collaborator_create(context, data_dict):
    '''Checks if a user is allowed to add collaborators to a dataset

    The current implementation restricts this ability to Administrators of the
    organization the dataset belongs to.
    '''

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
            'msg': toolkit._(
                'User %s not authorized to add members to this dataset') % user}

    return {'success': True}

