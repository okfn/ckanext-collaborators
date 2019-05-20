# encoding: utf-8

import datetime
import uuid
import logging
from collections import OrderedDict

from sqlalchemy import orm, Column, Unicode, DateTime
from sqlalchemy.ext.declarative import declarative_base

from ckan.model.meta import metadata

log = logging.getLogger(__name__)


def make_uuid():
    return unicode(uuid.uuid4())


Base = declarative_base(metadata=metadata)


class DatasetMember(Base):
    __tablename__ = u'dataset_member'

    id = Column(Unicode, primary_key=True, default=make_uuid)
    user_id = Column(Unicode, nullable=False)
    dataset_id = Column(Unicode, nullable=False)
    capacity = Column(Unicode, nullable=False)
    modified = Column(DateTime, default=datetime.datetime.utcnow)

    def as_dict(self):
        _dict = OrderedDict()
        table = orm.class_mapper(self.__class__).mapped_table
        for col in table.c:
            val = getattr(self, col.name)
            if isinstance(val, datetime.date):
                val = str(val)
            if isinstance(val, datetime.datetime):
                val = val.isoformat()
            _dict[col.name] = val
        return _dict

def create_tables():
    DatasetMember.__table__.create()

    log.info(u'Dataset collaborators database tables created')


def tables_exist():
    return DatasetMember.__table__.exists()
