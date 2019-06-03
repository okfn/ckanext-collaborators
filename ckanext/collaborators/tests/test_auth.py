from nose.tools import assert_equals, assert_raises

from ckan import model
from ckan.plugins import (
    toolkit, plugin_loaded,
    load as load_plugin, unload as unload_plugin)
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

    _load_plugins = ['image_view']

    def test_dataset_show_private_editor(self):

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

    def test_dataset_show_private_member(self):

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

    def test_resource_show_private_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_show',
            context=context, id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('resource_show',
            context=context, id=resource['id'])

    def test_resource_show_private_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_show',
            context=context, id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert helpers.call_auth('resource_show',
            context=context, id=resource['id'])

    def test_resource_view_list_private_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_view_list',
            context=context, id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('resource_view_list',
            context=context, id=resource['id'])

    def test_resource_view_list_private_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_view_list',
            context=context, id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert helpers.call_auth('resource_view_list',
            context=context, id=resource['id'])

    def test_resource_view_show_private_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        resource_view = factories.ResourceView(resource_id=resource['id'])
        user = factories.User()

        context = self._get_context(user)
        # Needed until ckan/ckan#4828 is backported
        context['resource'] = model.Resource.get(resource['id'])
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_view_show',
            context=context, id=resource_view['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('resource_view_show',
            context=context, id=resource_view['id'])

    def test_resource_view_show_private_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        resource_view = factories.ResourceView(resource_id=resource['id'])
        user = factories.User()

        context = self._get_context(user)
        # Needed until ckan/ckan#4828 is backported
        context['resource'] = model.Resource.get(resource['id'])
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_view_show',
            context=context, id=resource_view['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert helpers.call_auth('resource_view_show',
            context=context, id=resource_view['id'])

    def test_resource_view_show_private_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_view_list',
            context=context, id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('resource_show',
            context=context, id=resource['id'])


class TestCollaboratorsUpdate(CollaboratorsAuthTestBase, FunctionalTestBase):

    _load_plugins = ['image_view']

    def test_dataset_update_public_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'package_update',
            context=context, id=dataset['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('package_update',
            context=context, id=dataset['id'])

    def test_dataset_update_public_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'package_update',
            context=context, id=dataset['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'package_update',
            context=context, id=dataset['id'])


    def test_dataset_update_private_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'package_update',
            context=context, id=dataset['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('package_update',
            context=context, id=dataset['id'])

    def test_dataset_update_private_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'package_update',
            context=context, id=dataset['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'package_update',
            context=context, id=dataset['id'])

    def test_dataset_delete_private_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'package_delete',
            context=context, id=dataset['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('package_delete',
            context=context, id=dataset['id'])

    def test_dataset_delete_private_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'package_delete',
            context=context, id=dataset['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'package_delete',
            context=context, id=dataset['id'])

    def test_resource_create_public_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_create',
            context=context, package_id=dataset['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('resource_create',
            context=context, package_id=dataset['id'])

    def test_resource_create_public_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_create',
            context=context, package_id=dataset['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_create',
            context=context, package_id=dataset['id'])

    def test_resource_update_public_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_update',
            context=context, id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('resource_update',
            context=context, id=resource['id'])

    def test_resource_update_public_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_update',
            context=context, id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_update',
            context=context, id=resource['id'])

    def test_resource_delete_public_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_delete',
            context=context, id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('resource_delete',
            context=context, id=resource['id'])

    def test_resource_delete_public_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_delete',
            context=context, id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_delete',
            context=context, id=resource['id'])

    def test_resource_view_create_public_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_view_create',
            context=context, resource_id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('resource_view_create',
            context=context, resource_id=resource['id'])

    def test_resource_view_create_public_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_view_create',
            context=context, resource_id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'resource_view_create',
            context=context, resource_id=resource['id'])


class TestCollaboratorsDataStore(CollaboratorsAuthTestBase, FunctionalTestBase):

    _load_plugins = ['datastore']

    def test_datastore_search_private_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_search',
            context=context, resource_id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('datastore_search',
            context=context, resource_id=resource['id'])

    def test_datastore_search_private_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_search',
            context=context, resource_id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert helpers.call_auth('datastore_search',
            context=context, resource_id=resource['id'])

    def test_datastore_info_private_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_info',
            context=context, resource_id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('datastore_info',
            context=context, resource_id=resource['id'])

    def test_datastore_info_private_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_info',
            context=context, resource_id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert helpers.call_auth('datastore_info',
            context=context, resource_id=resource['id'])

    def test_datastore_search_sql_private_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        context['table_names'] = [resource['id']]
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_search_sql',
            context=context, sql='SELECT * FROM "{}"'.format(resource['id']))

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('datastore_search_sql',
            context=context, sql='SELECT * FROM "{}"'.format(resource['id']))

    def test_datastore_search_sql_private_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        context['table_names'] = [resource['id']]
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_search_sql',
            context=context, sql='SELECT * FROM "{}"'.format(resource['id']))

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert helpers.call_auth('datastore_search_sql',
            context=context, sql='SELECT * FROM "{}"'.format(resource['id']))


    def test_datastore_create_private_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_create',
            context=context, resource_id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('datastore_create',
            context=context, resource_id=resource['id'])

    def test_datastore_create_private_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_create',
            context=context, resource_id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_create',
            context=context, resource_id=resource['id'])

    def test_datastore_upsert_private_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_upsert',
            context=context, resource_id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('datastore_upsert',
            context=context, resource_id=resource['id'])

    def test_datastore_upsert_private_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_upsert',
            context=context, resource_id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_upsert',
            context=context, resource_id=resource['id'])

    def test_datastore_delete_private_editor(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_delete',
            context=context, resource_id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='editor')

        assert helpers.call_auth('datastore_delete',
            context=context, resource_id=resource['id'])

    def test_datastore_delete_private_member(self):

        org = factories.Organization()
        dataset = factories.Dataset(private=True, owner_org=org['id'])
        resource = factories.Resource(package_id=dataset['id'])
        user = factories.User()

        context = self._get_context(user)
        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_delete',
            context=context, resource_id=resource['id'])

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity='member')

        assert_raises(toolkit.NotAuthorized, helpers.call_auth,
            'datastore_delete',
            context=context, resource_id=resource['id'])
