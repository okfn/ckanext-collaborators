from flask.views import MethodView
import ckan.plugins.toolkit as toolkit

from ckan.common import _, g
import ckan.model as model
import ckan.lib.navl.dictization_functions as dictization_functions
import ckan.logic as logic



def collaborators(dataset_id):
    context = {u'model': model, u'user': toolkit.c.user}
    data_dict = {'id': dataset_id}
    
    # needed to ckan_extend package/edit_base.html
    try:    
        g.pkg_dict = toolkit.get_action('package_show')(context, data_dict)
    except (toolkit.NotAuthorized, toolkit.ObjectNotFound):
        message = 'Not found dataset "%s"'
        return toolkit.abort(404, message % (dataset_id))
    
    return toolkit.render('collaborator/collaborators.html')

def collaborator_delete(dataset_id, user_id):
    context = {u'model': model, u'user': toolkit.c.user}

    try:
        toolkit.get_action('dataset_collaborator_delete')(context, {
            'id': dataset_id,
            'user_id': user_id
        })
    except (toolkit.NotAuthorized, toolkit.ObjectNotFound):
        return toolkit.abort(404, toolkit._(u'Resource not found'))

    return toolkit.redirect_to(u'collaborators.read', dataset_id=dataset_id)

class CollaboratorEditView(MethodView):
    def post(self, dataset_id):
        context = {u'model': model, u'user': toolkit.c.user}
        
        try:
            form_dict = logic.clean_dict(
                dictization_functions.unflatten(
                    logic.tuplize_dict(logic.parse_params(toolkit.request.form))))
            
            data_dict = {
                'id': dataset_id,
                'user_id': form_dict['username'],
                'capacity': form_dict['capacity']
            }
            
            toolkit.get_action('dataset_collaborator_create')(context, data_dict)
        except dictization_functions.DataError:
            return toolkit.abort(400, _(u'Integrity Error'))
        except (toolkit.NotAuthorized, toolkit.ObjectNotFound):
            return toolkit.abort(404, toolkit._(u'Resource not found'))
        except toolkit.ValidationError:
            return toolkit.abort(404, toolkit._(u'Invalid capacity value'))

        return toolkit.redirect_to(u'collaborators.read', dataset_id=dataset_id)

    def get(self, dataset_id):
        context = {u'model': model, u'user': toolkit.c.user}
        data_dict = {'id': dataset_id}

        # needed to ckan_extend package/edit_base.html
        try:    
            g.pkg_dict = toolkit.get_action('package_show')(context, data_dict)
        except (toolkit.NotAuthorized, toolkit.ObjectNotFound):
            message = 'Not found dataset "%s"'
            return toolkit.abort(404, message % (dataset_id))
        
        user = toolkit.request.params.get(u'user_id')
        user_capacity = 'member'
        
        if user:
            collaborators = toolkit.get_action('dataset_collaborator_list')(context, data_dict)
            user_capacity = [c['capacity'] for c in collaborators if c['user_id'] == user][0]
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
        
        return toolkit.render('collaborator/collaborator_new.html', extra_vars)
