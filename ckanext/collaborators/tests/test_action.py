import mock

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

    def test_deleting_user_removes_collaborator(self):
        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'editor'

        member = helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity)

        assert_equals(model.Session.query(DatasetMember).count(), 1)

        helpers.call_action(
            'user_delete',
            id=user['id'])

        assert_equals(model.Session.query(DatasetMember).count(), 0)

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

    def test_list_for_user(self):

        dataset1 = factories.Dataset()
        dataset2 = factories.Dataset()
        user = factories.User()
        capacity1 = 'editor'
        capacity2 = 'member'

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset1['id'], user_id=user['id'], capacity=capacity1)

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset2['id'], user_id=user['id'], capacity=capacity2)

        datasets = helpers.call_action(
            'dataset_collaborator_list_for_user',
            id=user['id'])

        assert_equals(len(datasets), 2)

        assert_equals(datasets[0]['dataset_id'], dataset1['id'])
        assert_equals(datasets[0]['capacity'], capacity1)

        assert_equals(datasets[1]['dataset_id'], dataset2['id'])
        assert_equals(datasets[1]['capacity'], capacity2)

    def test_list_for_user_with_capacity(self):

        dataset1 = factories.Dataset()
        dataset2 = factories.Dataset()
        user = factories.User()
        capacity1 = 'editor'
        capacity2 = 'member'

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset1['id'], user_id=user['id'], capacity=capacity1)

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset2['id'], user_id=user['id'], capacity=capacity2)

        datasets = helpers.call_action(
            'dataset_collaborator_list_for_user',
            id=user['id'], capacity='editor')


        assert_equals(len(datasets), 1)

        assert_equals(datasets[0]['dataset_id'], dataset1['id'])
        assert_equals(datasets[0]['capacity'], capacity1)

    def test_list_for_user_user_not_found(self):

        assert_raises(toolkit.ObjectNotFound, helpers.call_action,
            'dataset_collaborator_list_for_user',
            id='xxx')

    def test_list_for_user_wrong_capacity(self):
        user = factories.User()
        capacity = 'unknown'

        assert_raises(toolkit.ValidationError, helpers.call_action,
            'dataset_collaborator_list_for_user',
            id=user['id'], capacity=capacity)


class TestCollaboratorsSearch(FunctionalTestBase):

    def test_search_results_editor(self):

        org = factories.Organization()
        dataset1 = factories.Dataset(
            name='test1', private=True, owner_org=org['id'])
        dataset2 = factories.Dataset(name='test2')

        user = factories.User()
        context = {'user': user['name']}

        results = toolkit.get_action('package_search')(context,
                {'q':'*:*', 'include_private':True})

        assert_equals(results['count'], 1)
        assert_equals(results['results'][0]['id'], dataset2['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset1['id'], user_id=user['id'], capacity='editor')

        results = toolkit.get_action('package_search')(context,
                {'q':'*:*', 'include_private':True, 'sort': 'name asc'})

        assert_equals(results['count'], 2)

        assert_equals(results['results'][0]['id'], dataset1['id'])
        assert_equals(results['results'][1]['id'], dataset2['id'])

    def test_search_results_member(self):

        org = factories.Organization()
        dataset1 = factories.Dataset(
            name='test1', private=True, owner_org=org['id'])
        dataset2 = factories.Dataset(name='test2')

        user = factories.User()
        context = {'user': user['name']}

        results = toolkit.get_action('package_search')(context,
                {'q':'*:*', 'include_private':True})

        assert_equals(results['count'], 1)
        assert_equals(results['results'][0]['id'], dataset2['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset1['id'], user_id=user['id'], capacity='member')

        results = toolkit.get_action('package_search')(context,
                {'q':'*:*', 'include_private':True, 'sort': 'name asc'})

        assert_equals(results['count'], 2)

        assert_equals(results['results'][0]['id'], dataset1['id'])
        assert_equals(results['results'][1]['id'], dataset2['id'])

    @mock.patch('ckanext.collaborators.mailer.mail_user')
    def test_create_collaborator_emails_notification_if_send_email(self, mock_mail_user):
        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'editor'

        member = helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity, send_mail=True)

        assert_equals(mock_mail_user.call_count, 1)

    @mock.patch('ckanext.collaborators.mailer.mail_user')
    def test_create_collaborator_emails_notification_if_not_send_email(self, mock_mail_user):
        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'editor'

        member = helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity, send_mail=False)

        assert_equals(mock_mail_user.call_count, 0)

    @mock.patch('ckanext.collaborators.mailer.mail_user')
    def test_delete_collaborators_emails_notification(self, mock_mail_user):
        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'editor'

        member = helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity, send_mail=True)

        helpers.call_action(
            'dataset_collaborator_delete',
            id=dataset['id'], user_id=user['id'])

        assert_equals(mock_mail_user.call_count, 2)
