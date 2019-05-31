from nose.tools import assert_equals, assert_raises

from ckan import model
from ckan.plugins import toolkit
from ckan.tests import helpers, factories

from ckanext.collaborators.tests import FunctionalTestBase


class CollaboratorsAuthTestBase(object):

    def _get_context(self, user):

        return {'model': model,
            'user': user if isinstance(user, basestring) else user.get('name')
        }


class TestCollaboratorsAuth(CollaboratorsAuthTestBase, FunctionalTestBase):

    def setup(self):

        super(TestCollaboratorsAuth, self).setup()

        self.org_admin  = factories.User()
        self.org_editor  = factories.User()
        self.org_member  = factories.User()

        self.normal_user  = factories.User()

        self.org = factories.Organization(
            users=[
                {'name': self.org_admin['name'], 'capacity': 'admin'},
                {'name': self.org_editor['name'], 'capacity': 'editor'},
                {'name': self.org_member['name'], 'capacity': 'member'},
            ]
        )

        self.dataset = factories.Dataset(owner_org=self.org['id'])

        self.org_admin2  = factories.User()
        self.org2 = factories.Organization(
            users=[
                {'name': self.org_admin2['name'], 'capacity': 'admin'},
            ]
        )

    def test_create_org_admin_is_authorized(self):

        context = self._get_context(self.org_admin)
        assert helpers.call_auth('dataset_collaborator_create',
            context=context, id=self.dataset['id'])

    def test_create_org_editor_is_not_authorized(self):

        context = self._get_context(self.org_editor)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_create',
            context=context, id=self.dataset['id'])

    def test_create_org_member_is_not_authorized(self):

        context = self._get_context(self.org_member)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_create',
            context=context, id=self.dataset['id'])

    def test_create_org_admin_from_other_org_is_not_authorized(self):

        context = self._get_context(self.org_admin2)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_create',
            context=context, id=self.dataset['id'])

    def test_create_missing_org_is_not_authorized(self):

        dataset = factories.Dataset(owner_org=None)

        context = self._get_context(self.org_admin)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_create',
            context=context, id=dataset['id'])

    def test_delete_org_admin_is_authorized(self):

        context = self._get_context(self.org_admin)
        assert helpers.call_auth('dataset_collaborator_delete',
            context=context, id=self.dataset['id'])

    def test_delete_org_editor_is_not_authorized(self):

        context = self._get_context(self.org_editor)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_delete',
            context=context, id=self.dataset['id'])

    def test_delete_org_member_is_not_authorized(self):

        context = self._get_context(self.org_member)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_delete',
            context=context, id=self.dataset['id'])

    def test_delete_org_admin_from_other_org_is_not_authorized(self):

        context = self._get_context(self.org_admin2)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_delete',
            context=context, id=self.dataset['id'])

    def test_delete_missing_org_is_not_authorized(self):

        dataset = factories.Dataset(owner_org=None)

        context = self._get_context(self.org_admin)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_delete',
            context=context, id=dataset['id'])

    def test_list_org_admin_is_authorized(self):

        context = self._get_context(self.org_admin)
        assert helpers.call_auth('dataset_collaborator_list',
            context=context, id=self.dataset['id'])

    def test_list_org_editor_is_not_authorized(self):

        context = self._get_context(self.org_editor)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_list',
            context=context, id=self.dataset['id'])

    def test_list_org_member_is_not_authorized(self):

        context = self._get_context(self.org_member)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_list',
            context=context, id=self.dataset['id'])

    def test_list_org_admin_from_other_org_is_not_authorized(self):

        context = self._get_context(self.org_admin2)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_list_for_user',
            context=context, id=self.dataset['id'])

    def test_user_list_own_user_is_authorized(self):

        context = self._get_context(self.normal_user)
        assert helpers.call_auth('dataset_collaborator_list_for_user',
            context=context, id=self.normal_user['id'])

    def test_user_list_org_admin_is_not_authorized(self):

        context = self._get_context(self.org_admin)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_list_for_user',
            context=context, id=self.normal_user['id'])

    def test_user_list_org_editor_is_not_authorized(self):

        context = self._get_context(self.org_editor)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_list_for_user',
            context=context, id=self.normal_user['id'])

    def test_user_list_org_member_is_not_authorized(self):

        context = self._get_context(self.org_member)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_list_for_user',
            context=context, id=self.normal_user['id'])

    def test_user_list_org_admin_from_other_org_is_not_authorized(self):

        context = self._get_context(self.org_admin2)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'dataset_collaborator_list_for_user',
            context=context, id=self.normal_user['id'])


class TestCollaboratorsShow(CollaboratorsAuthTestBase, FunctionalTestBase):

    def test_show_private_dataset_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'package_show',
            context=context, id=dataset['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('package_show',
            context=context, id=dataset['id'])

    def test_show_private_dataset_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'package_show',
            context=context, id=dataset['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert helpers.call_auth('package_show',
            context=context, id=dataset['id'])
