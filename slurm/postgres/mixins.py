"""
Postgres mixins
"""
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import ARRAY
from contextlib import contextmanager

class StatusTypeMixin(object):
    """ Gather information about processing status """
    id             = Column(Integer, primary_key=True)
    job_id         = Column(Integer)
    program        = Column(String)
    project        = Column(String)
    case_id        = Column(String)
    location       = Column(String)
    status         = Column(String)
    datetime_now   = Column(String)
    hostname       = Column(String)
    docker         = Column(ARRAY(String))
    elapsed        = Column(Float)
    thread_count   = Column(Integer)

    def __repr__(self):
        return "<StatusTypeMixin(case_id='%s', status='%s' , location='%s'>" %(self.case_id,
                self.status, self.location)
