from flask import Blueprint
from ckanext.collaborators.views.package import (collaborators,
collaborator_delete, CollaboratorEditView
)


collaborators_blueprint = Blueprint('collaborators', __name__)

collaborators_blueprint.add_url_rule(
    rule=u'/datasets/collaborators/<dataset_id>',
    endpoint='read',
    view_func=collaborators, methods=['GET',]
    )

collaborators_blueprint.add_url_rule(
    rule=u'/datasets/collaborators/<dataset_id>/new',
    view_func=CollaboratorEditView.as_view('new'), 
    methods=['GET', 'POST',]
    )

collaborators_blueprint.add_url_rule(
    rule=u'/datasets/collaborators/<dataset_id>/delete/<user_id>',
    endpoint='delete',
    view_func=collaborator_delete, methods=['POST',]
    )