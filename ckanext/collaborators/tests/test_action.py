from nose.tools import assert_equals, assert_raises

from ckan import model
from ckan.plugins import toolkit
from ckan.tests import helpers, factories

from ckanext.collaborators.model import DatasetMember
from ckanext.collaborators.tests import FunctionalTestBase


class TestCollaboratorsActions(FunctionalTestBase):

    def test_create(self):

        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'editor'

        member = helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity)

        assert_equals(member['dataset_id'], dataset['id'])
        assert_equals(member['user_id'], user['id'])
        assert_equals(member['capacity'], capacity)

        assert_equals(model.Session.query(DatasetMember).count(), 1)

    def test_update(self):

        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'editor'

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity)

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert_equals(model.Session.query(DatasetMember).count(), 1)

        assert_equals(model.Session.query(DatasetMember).one().capacity,
            'member')

    def test_create_wrong_capacity(self):
        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'unknown'

        assert_raises(toolkit.ValidationError, helpers.call_action,
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity)

    def test_create_dataset_not_found(self):
        dataset = {'id': 'xxx'}
        user = factories.User()
        capacity = 'editor'

        assert_raises(toolkit.ObjectNotFound, helpers.call_action,
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity)

    def test_create_user_not_found(self):
        dataset = factories.Dataset()
        user = {'id': 'yyy'}
        capacity = 'editor'

        assert_raises(toolkit.ObjectNotFound, helpers.call_action,
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity)

    def test_delete(self):

        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'editor'

        member = helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity)

        assert_equals(model.Session.query(DatasetMember).count(), 1)

        helpers.call_action(
            'dataset_collaborator_delete',
            id=dataset['id'], user_id=user['id'])

        assert_equals(model.Session.query(DatasetMember).count(), 0)

    def test_delete_dataset_not_found(self):
        dataset = {'id': 'xxx'}
        user = factories.User()

        assert_raises(toolkit.ObjectNotFound, helpers.call_action,
            'dataset_collaborator_delete',
            id=dataset['id'], user_id=user['id'])

    def test_delete_user_not_found(self):
        dataset = factories.Dataset()
        user = {'id': 'yyy'}

        assert_raises(toolkit.ObjectNotFound, helpers.call_action,
            'dataset_collaborator_delete',
            id=dataset['id'], user_id=user['id'])

    def test_list(self):

        dataset = factories.Dataset()
        user1 = factories.User()
        capacity1 = 'editor'
        user2 = factories.User()
        capacity2 = 'member'

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user1['id'], capacity=capacity1)

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user2['id'], capacity=capacity2)

        members = helpers.call_action(
            'dataset_collaborator_list',
            id=dataset['id'])


        assert_equals(len(members), 2)

        assert_equals(members[0]['dataset_id'], dataset['id'])
        assert_equals(members[0]['user_id'], user1['id'])
        assert_equals(members[0]['capacity'], capacity1)

        assert_equals(members[1]['dataset_id'], dataset['id'])
        assert_equals(members[1]['user_id'], user2['id'])
        assert_equals(members[1]['capacity'], capacity2)

    def test_list_with_capacity(self):

        dataset = factories.Dataset()
        user1 = factories.User()
        capacity1 = 'editor'
        user2 = factories.User()
        capacity2 = 'member'

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user1['id'], capacity=capacity1)

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user2['id'], capacity=capacity2)

        members = helpers.call_action(
            'dataset_collaborator_list',
            id=dataset['id'], capacity='member')


        assert_equals(len(members), 1)

        assert_equals(members[0]['dataset_id'], dataset['id'])
        assert_equals(members[0]['user_id'], user2['id'])
        assert_equals(members[0]['capacity'], capacity2)

    def test_list_dataset_not_found(self):

        assert_raises(toolkit.ObjectNotFound, helpers.call_action,
            'dataset_collaborator_list',
            id='xxx')

    def test_list_wrong_capacity(self):
        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'unknown'

        assert_raises(toolkit.ValidationError, helpers.call_action,
            'dataset_collaborator_list',
            id=dataset['id'], user_id=user['id'], capacity=capacity)
