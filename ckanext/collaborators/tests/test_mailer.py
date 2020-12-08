# -*- coding: utf-8 -*-

from nose.tools import assert_equals, assert_raises
import mock
from ckan.tests import helpers, factories
from ckan import model

from ckanext.collaborators.model import DatasetMember
from ckanext.collaborators.tests import FunctionalTestBase
from ckanext.collaborators import mailer


class TestCollaboratorsMailer(FunctionalTestBase):

    @mock.patch('ckanext.collaborators.mailer.mail_user')
    def test_email_notification_create(self, mock_mail_user):
        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'editor'

        mailer.mail_notification_to_collaborator(
            dataset['id'], user['id'], capacity, 'create')

        assert_equals(mock_mail_user.call_count, 1)

    @mock.patch('ckanext.collaborators.mailer.mail_user')
    def test_email_notification_delete(self, mock_mail_user):
        dataset = factories.Dataset()
        user = factories.User()
        capacity = 'editor'

        mailer.mail_notification_to_collaborator(
            dataset['id'], user['id'], capacity, 'delete')

        assert_equals(mock_mail_user.call_count, 1)

    def test_subject_unicode(self):
        dataset = factories.Dataset(title=u'réfugiés')
        subject = mailer._compose_email_subj(model.Package.get(dataset['id']))
        assert u'réfugiés' in subject
