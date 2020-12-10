import logging
from ckan import model as core_model
from ckan.plugins import toolkit
from ckan.lib.mailer import mail_user, MailerException
from ckan.lib.base import render_jinja2
log = logging.getLogger(__name__)


def _compose_email_subj(dataset):
    return u'{0} - Notification about collaborator role for {1}'.format(
        toolkit.config.get('ckan.site_title'), dataset.title)

def _compose_email_body(user, dataset, role, event):
    dataset_link = toolkit.url_for('dataset_read', id=dataset.id, qualified=True)
    return render_jinja2('collaborators/emails/{0}_collaborator.html'.format(event), {
        'user_name': user.fullname or user.name,
        'role': role,
        'site_title': toolkit.config.get('ckan.site_title'),
        'site_url': toolkit.config.get('ckan.site_url'),
        'dataset_title': dataset.title,
        'dataset_link': dataset_link
    })

def mail_notification_to_collaborator(dataset_id, user_id, capacity, event):
    user = core_model.User.get(user_id)
    dataset = core_model.Package.get(dataset_id)

    try:
        subj = _compose_email_subj(dataset)
        body = _compose_email_body(user, dataset, capacity, event)
        mail_user(user, subj, body, headers={
            'Content-Type': 'text/html; charset=UTF-8'
        })
    except MailerException as exception:
        log.exception(exception)
