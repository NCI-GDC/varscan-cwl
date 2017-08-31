'''
Postgres mixins
'''
from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.dialects.postgresql import ARRAY
from contextlib import contextmanager

class StatusTypeMixin(object):
    """ Gather information about processing status """
    id               = Column(Integer, primary_key=True)
    case_id          = Column(String)
    tumor_gdc_id     = Column(String)
    normal_gdc_id    = Column(String)
    output_id        = Column(String)
    status           = Column(String)
    s3_url           = Column(String)
    datetime_start   = Column(String)
    datetime_end     = Column(String)
    md5              = Column(String)
    file_size        = Column(String)
    hostname         = Column(String)
    cwl_version      = Column(String)
    docker_version   = Column(ARRAY(String))

    def __repr__(self):
        return "<StatusTypeMixin(uuid='%s', status='%s' , s3_url='%s')>" %(self.uuid, self.status, self.s3_url)

class MetricsTypeMixin(object):
    ''' Gather timing metrics with input uuids '''
    id                                 = Column(Integer, primary_key=True)
    case_id                            = Column(String)
    tumor_gdc_id                       = Column(String)
    normal_gdc_id                      = Column(String)
    download_time                      = Column(String)
    upload_time                        = Column(String)
    thread_count                       = Column(String)
    whole_workflow_elapsed             = Column(String)
    avg_cwl_systime                   = Column(Float)
    avg_cwl_usertime                  = Column(Float)
    avg_cwl_walltime                  = Column(Float)
    avg_cwl_percent_of_cpu            = Column(Float)
    avg_cwl_maximum_resident_set_size = Column(Float)
    status                             = Column(String)

    def __repr__(self):
        return "<TimeToolTypeMixin(uuid='%s', elapsed='%s', status='%s')>" %(self.uuid, self.elapsed, self.status)
