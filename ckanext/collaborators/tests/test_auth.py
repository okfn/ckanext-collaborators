from nose.tools import assert_equals, assert_raises

from ckan import model
from ckan.plugins import toolkit
from ckan.tests import helpers, factories

from ckanext.collaborators.tests import FunctionalTestBase


class TestCollaboratorsAuth(FunctionalTestBase):

    def setup(self):

        super(TestCollaboratorsAuth, self).setup()

        self.org_admin  = factories.User()
        self.org_editor  = factories.User()
        self.org_member  = factories.User()


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

    def _get_context(self, user):

        return {'model': model,
            'user': user if isinstance(user, basestring) else user.get('name')
        }

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
