from nose.tools import assert_equals, assert_raises
import mock
from ckan.tests import helpers, factories
from ckan import model

from ckanext.collaborators.model import DatasetMember
from ckanext.collaborators.tests import FunctionalTestBase
from ckanext.collaborators.mailer import mail_notification_to_collaborator


class TestCollaboratorsMailer(FunctionalTestBase):

    @mock.patch('ckanext.collaborators.mailer.mail_user')
    def test_email_notification_create(self, mock_mail_user):
        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'editor' 

        mail_notification_to_collaborator(
            dataset['id'], user['id'], capacity, 'create')
        
        assert_equals(mock_mail_user.call_count, 1)

    @mock.patch('ckanext.collaborators.mailer.mail_user')
    def test_email_notification_delete(self, mock_mail_user):
        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'editor' 

        mail_notification_to_collaborator(
            dataset['id'], user['id'], capacity, 'delete')
        
        assert_equals(mock_mail_user.call_count, 1)