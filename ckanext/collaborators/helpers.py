import ckan.plugins.toolkit as toolkit

def get_collaborators(package_dict):
    '''Return collaborators list.
    '''
    context = {'ignore_auth': True} #TODO
    data_dict = {'id': package_dict['id']}
    _collaborators = toolkit.get_action('dataset_collaborator_list')(context, data_dict)
    
    collaborators = []

    for collaborator in _collaborators:
        collaborators.append([
            collaborator['user_id'],
            collaborator['capacity']
            ])

    return collaborators

