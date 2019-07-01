from nose.tools import assert_in, assert_not_in, assert_equal

from ckan.tests import helpers, factories
from ckan.plugins import toolkit

submit_and_follow = helpers.submit_and_follow

class TestCollaborators(helpers.FunctionalTestBase):

    def setup(self):

        super(TestCollaborators, self).setup()

        self.org_admin = factories.User()
        self.org_admin_name = self.org_admin['name'].encode('ascii')

        self.org_member = factories.User()
        self.org_member_name = self.org_member['name'].encode('ascii')

        self.org_editor = factories.User()
        self.org_editor_name = self.org_editor['name'].encode('ascii')


        self.org = factories.Organization(
            users=[
                {'name': self.org_member['name'], 'capacity': 'member'},
                {'name': self.org_editor['name'], 'capacity': 'editor'},
                {'name': self.org_admin['name'], 'capacity': 'admin'},
            ]
        )

    def test_show_collaborator_tab_for_org_admins(self):
        dataset = factories.Dataset(
                private=True,
                owner_org=self.org['id'],
        )

        url = toolkit.url_for('dataset_edit', id=dataset['id'])

        app = self._get_test_app()

        environ = {'REMOTE_USER': self.org_admin_name}
        res = app.get(url, extra_environ=environ)

        assert_in('<li><a href="/dataset/collaborators/', res.body)

    def test_editor_collaborators_are_shown(self):
        dataset = factories.Dataset(
                private=True,
                owner_org=self.org['id'],
        )
        user = factories.User(fullname='Editor Collaborator')
        capacity = 'editor'

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity)

        # TODO: Replace with toolkit.url_for()
        url = '/dataset/collaborators/{id}'.format(id=dataset['id'])
        
        app = self._get_test_app()
        environ = {'REMOTE_USER': self.org_admin_name}
        res = app.get(url, extra_environ=environ)

        assert_in('Editor Collaborator', res.body)
        assert_in('<td>editor</td>', res.body)

    def test_member_collaborators_are_shown(self):
        dataset = factories.Dataset(
                private=True,
                owner_org=self.org['id'],
        )
        user = factories.User(fullname='Member Collaborator')
        capacity = 'member'
        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity)

        # TODO: Replace with toolkit.url_for()
        url = '/dataset/collaborators/{id}'.format(id=dataset['id'])
        
        app = self._get_test_app()
        environ = {'REMOTE_USER': self.org_admin_name}
        res = app.get(url, extra_environ=environ)

        assert_in('Member Collaborator', res.body)
        assert_in('<td>member</td>', res.body)

    
    def test_collaborators_can_read_private_datasets(self):
        collaborators = {
            'member': factories.User(),
            'editor': factories.User()
        }
        
        dataset = factories.Dataset(
            owner_org=self.org['id'],
            private=True,
        )
        app = self._get_test_app()

        for capacity, user_dict in collaborators.items():
            helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user_dict['id'], capacity=capacity)

            res = app.get(
                toolkit.url_for(
                    'dataset_read',
                    id=dataset['name']
                ),
                extra_environ={
                    'REMOTE_USER': user_dict['name'].encode('ascii'),
                },
            )
            assert_in('Test Dataset', res.body)
            assert_in('Just another test dataset', res.body)

    def test_editor_collaborator_can_edit_private_datasets(self):
        user = factories.User()
        dataset = factories.Dataset(
                private=True,
                owner_org=self.org['id'],
        )
        capacity = 'editor'

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity)

        app = self._get_test_app()
        env = {'REMOTE_USER': user['name'].encode('ascii')}
        res = app.get(
            toolkit.url_for('dataset_edit',
                    id=dataset['name']),
            extra_environ=env,
        )
        form = res.forms['dataset-edit']
        form['notes'] = u'edited description'
        submit_and_follow(app, form, env, 'save')

        result = helpers.call_action('package_show', id=dataset['id'])
        assert_equal(u'edited description', result['notes'])
    
    def test_member_collaborator_cannot_edit_private_datasets(self):
        user = factories.User()
        dataset = factories.Dataset(
                private=True,
                owner_org=self.org['id'],
        )
        capacity = 'member'

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity)

        app = self._get_test_app()
        env = {'REMOTE_USER': user['name'].encode('ascii')}
        
        res = app.get(
            toolkit.url_for('dataset_edit',
                    id=dataset['name']),
            extra_environ=env,
            status=403,
        )

        res = app.post(
            toolkit.url_for('dataset_edit',
                    id=dataset['name']),
            {'notes': 'edited description'},
            extra_environ=env,
            status=403,
        )

    def test_org_members_cannot_add_collaborators(self):
        dataset = factories.Dataset(
                private=True,
                owner_org=self.org['id'],
        )
        new_collaborator = factories.User()

        org_members = {
            'member': self.org_member_name,
            'editor': self.org_editor_name
        }

        app = self._get_test_app()
        url = '/dataset/collaborators/{id}/new'.format(id=dataset['id'])

        for member_name in org_members.values():
            env = {'REMOTE_USER': member_name}

            res = app.get(
                    url,
                    extra_environ=env,
                    status=401, )
            res = app.post(
                    url,
                    {
                        'id': dataset['id'],
                        'username': new_collaborator['name'].encode('ascii'),
                        'capacity': 'member'
                    },
                    extra_environ=env,
                    status=401, )

    def test_org_members_cannot_read_collaborators(self):
        dataset = factories.Dataset(
                private=True,
                owner_org=self.org['id'],
        )

        org_members = {
            'member': self.org_member_name,
            'editor': self.org_editor_name
        }

        app = self._get_test_app()
        url = '/dataset/collaborators/{id}'.format(id=dataset['id'])

        for member_name in org_members.values():
            env = {'REMOTE_USER': member_name}

            res = app.get(
                    url,
                    extra_environ=env,
                    status=401, )

    def test_org_members_cannot_delete_collaborators(self):
        dataset = factories.Dataset(
                private=True,
                owner_org=self.org['id'],
        )
        new_collaborator = factories.User()
        capacity = 'member'

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=new_collaborator['id'], capacity=capacity)

        org_members = {
            'member': self.org_member_name,
            'editor': self.org_editor_name
        }

        app = self._get_test_app()
        url = '/dataset/collaborators/{id}/delete/{collaborator}'.format(
            id=dataset['id'], collaborator= new_collaborator['id'])

        for member_name in org_members.values():
            env = {'REMOTE_USER': member_name}

            res = app.post(
                    url,
                    {
                        'id': dataset['id'],
                        'user_id': new_collaborator['id'],
                    },
                    extra_environ=env,
                    status=401, )

    def test_org_admins_can_delete_collaborators(self):
        dataset = factories.Dataset(
                private=True,
                owner_org=self.org['id'],
        )
        user = factories.User()
        capacity = 'member'

        helpers.call_action(
            'dataset_collaborator_create',
            id=dataset['id'], user_id=user['id'], capacity=capacity)

        app = self._get_test_app()
        url = '/dataset/collaborators/{id}/delete/{collaborator}'.format(
            id=dataset['id'], collaborator= user['id'])
        
        env = {'REMOTE_USER': self.org_admin_name}

        res = app.post(
                url,
                {
                    'id': dataset['id'],
                    'user_id': user['id'],
                },
                extra_environ=env,
                status=302, )
