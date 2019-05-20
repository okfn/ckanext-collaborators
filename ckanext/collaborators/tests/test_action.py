from nose.tools import assert_equals, assert_raises

from ckan.plugins import toolkit
from ckan.tests import helpers, factories

from ckanext.collaborators.tests import FunctionalTestBase


class TestCollaboratorsLogic(FunctionalTestBase):

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

