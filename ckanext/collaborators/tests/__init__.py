from ckan.tests import helpers

from ckanext.collaborators.model import tables_exist, create_tables

class FunctionalTestBase(helpers.FunctionalTestBase):

    @classmethod
    def setup_class(cls):

        super(FunctionalTestBase, cls).setup_class()

        if not tables_exist():
            create_tables()
