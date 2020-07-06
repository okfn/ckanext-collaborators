from flask import Blueprint
from flask.views import MethodView

from ckan.common import _, g

import ckan.plugins.toolkit as toolkit
import ckan.model as model
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.logic as logic


def collaborators_read(dataset_id):
    if not hasattr(toolkit.c, 'user') or not toolkit.c.user:
        return toolkit.abort(401, 'Unauthorized')

    context = {u'model': model, u'user': toolkit.c.user}
    data_dict = {'id': dataset_id}

    try:
        toolkit.check_access(u'dataset_collaborator_list', context, data_dict)
        # needed to ckan_extend package/edit_base.html
        g.pkg_dict = toolkit.get_action('package_show')(context, data_dict)
    except toolkit.NotAuthorized:
        message = 'Unauthorized to read collaborators {0}'.format(dataset_id)
        return toolkit.abort(403, toolkit._(message))
    except toolkit.ObjectNotFound:
        return toolkit.abort(404, toolkit._(u'Resource not found'))

    return toolkit.render('collaborators/collaborator/collaborators.html')

def collaborator_delete(dataset_id, user_id):
    if not hasattr(toolkit.c, 'user') or not toolkit.c.user:
        return toolkit.abort(401, 'Unauthorized')

    context = {u'model': model, u'user': toolkit.c.user}

    try:
        toolkit.get_action('dataset_collaborator_delete')(context, {
            'id': dataset_id,
            'user_id': user_id
        })
    except toolkit.NotAuthorized:
        message = u'Unauthorized to delete collaborators {0}'.format(dataset_id)
        return toolkit.abort(403, toolkit._(message))
    except toolkit.ObjectNotFound as e:
        return toolkit.abort(404, toolkit._(e.message))

    toolkit.h.flash_success(toolkit._('User removed from collaborators'))

    return toolkit.redirect_to(u'collaborators.read', dataset_id=dataset_id)

class CollaboratorEditView(MethodView):
    def post(self, dataset_id):
        if not hasattr(toolkit.c, 'user') or not toolkit.c.user:
            return toolkit.abort(401, 'Unauthorized')

        context = {u'model': model, u'user': toolkit.c.user}

        try:
            form_dict = logic.clean_dict(
                dictization_functions.unflatten(
                    logic.tuplize_dict(
                        logic.parse_params(toolkit.request.form))))

            user = toolkit.get_action('user_show')(context, {
                'id':form_dict['username']
                })

            data_dict = {
                'id': dataset_id,
                'user_id': user['id'],
                'capacity': form_dict['capacity'],
                'send_mail': form_dict.get('send_mail', False)
            }

            toolkit.get_action('dataset_collaborator_create')(
                context, data_dict)

        except dictization_functions.DataError:
            return toolkit.abort(400, _(u'Integrity Error'))
        except toolkit.NotAuthorized:
            message = u'Unauthorized to edit collaborators {0}'.format(dataset_id)
            return toolkit.abort(403, toolkit._(message))
        except toolkit.ObjectNotFound:
            return toolkit.abort(404, toolkit._(u'Resource not found'))
        except toolkit.ValidationError as e:
            toolkit.h.flash_error(e.error_summary)
        else:
            toolkit.h.flash_success(toolkit._('User added to collaborators'))

        return toolkit.redirect_to(u'collaborators.read', dataset_id=dataset_id)

    def get(self, dataset_id):
        if not hasattr(toolkit.c, 'user') or not toolkit.c.user:
            return toolkit.abort(401, 'Unauthorized')

        context = {u'model': model, u'user': toolkit.c.user}
        data_dict = {'id': dataset_id}

        try:
            toolkit.check_access(u'dataset_collaborator_list', context, data_dict)
            # needed to ckan_extend package/edit_base.html
            g.pkg_dict = toolkit.get_action('package_show')(context, data_dict)
        except toolkit.NotAuthorized:
            message = u'Unauthorized to read collaborators {0}'.format(dataset_id)
            return toolkit.abort(403, toolkit._(message))
        except toolkit.ObjectNotFound as e:
            return toolkit.abort(404, toolkit._(u'Resource not found'))

        user = toolkit.request.params.get(u'user_id')
        user_capacity = 'member'

        if user:
            collaborators = toolkit.get_action('dataset_collaborator_list')(
                context, data_dict)
            for c in collaborators:
                if c['user_id'] == user:
                    user_capacity = c['capacity']
            user = toolkit.get_action('user_show')(context, {'id': user})
            # Needed to reuse template
            g.user_dict = user

        extra_vars = {
            'capacities': [
                {'name':'editor', 'value': 'editor'},
                {'name':'member', 'value':'member'}
                ],
            'user_capacity': user_capacity,
        }

        return toolkit.render('collaborators/collaborator/collaborator_new.html', extra_vars)


collaborators = Blueprint('collaborators', __name__)

collaborators.add_url_rule(
    rule=u'/dataset/collaborators/<dataset_id>',
    endpoint='read',
    view_func=collaborators_read, methods=['GET',]
    )

collaborators.add_url_rule(
    rule=u'/dataset/collaborators/<dataset_id>/new',
    view_func=CollaboratorEditView.as_view('new'),
    methods=['GET', 'POST',]
    )

collaborators.add_url_rule(
    rule=u'/dataset/collaborators/<dataset_id>/delete/<user_id>',
    endpoint='delete',
    view_func=collaborator_delete, methods=['POST',]
    )
