import logging
import datetime

from ckan import model as core_model
from ckan.plugins import toolkit

from ckanext.collaborators.model import DatasetMember

log = logging.getLogger(__name__)


ALLOWED_CAPACITIES = ('editor', 'member')


def dataset_collaborator_create(context, data_dict):
    '''Make a user a collaborator in a dataset.

    If the user is already a collaborator in the dataset then their
    capacity will be updated.

    Currently you must be an Admin on the dataset owner organization to
    manage collaborators.

    :param id: the id or name of the dataset
    :type id: string
    :param user_id: the id or name of the user to add or edit
    :type object: string
    :param capacity: the capacity of the membership. Must be one of {}
    :type capacity: string

    :returns: the newly created (or updated) collaborator
    :rtype: dictionary

    '''.format(', '.join(ALLOWED_CAPACITIES))

    model = context.get('model', core_model)

    dataset_id, user_id, capacity = toolkit.get_or_bust(data_dict,
        ['id', 'user_id', 'capacity'])

    if capacity not in ALLOWED_CAPACITIES:
        raise toolkit.ValidationError(
            'Capacity must be one of "{}"'.format(', '.join(
                ALLOWED_CAPACITIES)))

    dataset = model.Package.get(dataset_id)
    if not dataset:
        raise toolkit.ObjectNotFound('Dataset not found')

    user = model.User.get(user_id)
    if not user:
        raise toolkit.ObjectNotFound('User not found')

    toolkit.check_access('dataset_collaborator_create', context, data_dict)

    # Check if member already exists
    member = model.Session.query(DatasetMember).\
        filter(DatasetMember.dataset_id == dataset.id).\
        filter(DatasetMember.user_id == user.id).one_or_none()
    if not member:
        member = DatasetMember(dataset_id=dataset_id,
                              user_id=user_id)
    member.capacity = capacity
    member.modified = datetime.datetime.utcnow()

    model.Session.add(member)
    model.repo.commit()

    log.info('User {} added as collaborator in dataset {} ({})'.format(
        user.name, dataset.id, capacity))

    return member.as_dict()


def dataset_collaborator_delete(context, data_dict):
    '''Remove a collaborator from a dataset.

    Currently you must be an Admin on the dataset owner organization to
    manage collaborators.

    :param id: the id or name of the dataset
    :type id: string
    :param user_id: the id or name of the user to remove
    :type object: string

    '''
    model = context.get('model', core_model)

    dataset_id, user_id = toolkit.get_or_bust(data_dict,
        ['id', 'user_id'])

    dataset = model.Package.get(dataset_id)
    if not dataset:
        raise toolkit.ObjectNotFound('Dataset not found')

    toolkit.check_access('dataset_collaborator_delete', context, data_dict)

    member = model.Session.query(DatasetMember).\
        filter(DatasetMember.dataset_id == dataset.id).\
        filter(DatasetMember.user_id == user_id).one_or_none()
    if not member:
        raise toolkit.ObjectNotFound(
            'User {} is not a collaborator on this dataset'.format(user_id))

    model.Session.delete(member)
    model.repo.commit()

    log.info('User {} removed as collaborator from dataset {}'.format(
        user_id, dataset.id))


def dataset_collaborator_list(context, data_dict):
    '''Return the list of all collaborators for a given dataset.

    Currently you must be an Admin on the dataset owner organization to
    manage collaborators.

    :param id: the id or name of the dataset
    :type id: string
    :param capacity: (optional) If provided, only users with this capacity are
        returned
    :type id: string

    :returns: a list of collaborators, each a dict including the dataset and
        user id, the capacity and the last modified date
    :rtype: list of dictionaries

    '''

    model = context.get('model', core_model)

    dataset_id = toolkit.get_or_bust(data_dict,'id')

    dataset = model.Package.get(dataset_id)
    if not dataset:
        raise toolkit.ObjectNotFound('Dataset not found')

    toolkit.check_access('dataset_collaborator_list', context, data_dict)

    capacity = data_dict.get('capacity')
    if capacity and capacity not in ALLOWED_CAPACITIES:
        raise toolkit.ValidationError(
            'Capacity must be one of "{}"'.format(', '.join(
                ALLOWED_CAPACITIES)))
    q = model.Session.query(DatasetMember).\
        filter(DatasetMember.dataset_id == dataset.id)

    if capacity:
        q = q.filter(DatasetMember.capacity == capacity)

    members = q.all()

    return [member.as_dict() for member in members]


def dataset_collaborator_list_for_user(context, data_dict):
    '''Return a list of all dataset the user is a collaborator in

    :param id: the id or name of the user
    :type id: string
    :param capacity: (optional) If provided, only datasets where the user has this
        capacity are returned
    :type capacity: string

    :returns: a list of datasets, each a dict including the dataset id, the
        capacity and the last modified date
    :rtype: list of dictionaries

    '''
    model = context.get('model', core_model)

    user_id = toolkit.get_or_bust(data_dict,'id')

    user = model.User.get(user_id)
    if not user:
        raise toolkit.ObjectNotFound('User not found')

    toolkit.check_access('dataset_collaborator_list_for_user', context, data_dict)

    capacity = data_dict.get('capacity')
    if capacity and capacity not in ALLOWED_CAPACITIES:
        raise toolkit.ValidationError(
            'Capacity must be one of "{}"'.format(', '.join(
                ALLOWED_CAPACITIES)))
    q = model.Session.query(DatasetMember).\
        filter(DatasetMember.user_id == user.id)

    if capacity:
        q = q.filter(DatasetMember.capacity == capacity)

    members = q.all()

    out = []
    for member in members:
        out.append({
            'dataset_id': member.dataset_id,
            'capacity': member.capacity,
            'modified': member.modified.isoformat(),
        })

    return out
