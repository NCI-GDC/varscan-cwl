'''
Postgres tables for the raw VCF from varscan indel CWL Workflow
'''
from postgres.mixins import StatusTypeMixin
import postgres.utils

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Column, Integer, String, Float, cast

class VcfStatus(StatusTypeMixin, postgres.utils.Base):

    __tablename__                = 'varscan_indel_recover_20170629_cwl_status' 
    tumor_bam_uuid               = Column(String)
    normal_bam_uuid              = Column(String)
    src_vcf_id                   = Column(String)
    raw_vcf_id                   = Column(String)
    annotated_vcf_id             = Column(String)
    raw_vcf_filename             = Column(String)
    raw_vcf_index_filename       = Column(String)
    annotated_vcf_filename       = Column(String)
    annotated_vcf_index_filename = Column(String)
    raw_md5                      = Column(ARRAY(String))
    annotated_md5                = Column(ARRAY(String))

def add_vcf_status(engine, table, data):
    """ add provided status metrics to database """
    met = table(
              job_id                       = data['job_id'],
              program                      = data['program'],
              project                      = data['project'],
              case_id                      = data['case_id'],
              tumor_bam_uuid               = data['tumor_bam_uuid'],
              normal_bam_uuid              = data['normal_bam_uuid'],
              status                       = data['status'],
              src_vcf_id                   = data['src_vcf_id'],
              location                     = data['location'],
              raw_vcf_filename             = data['raw_vcf_filename'],
              raw_vcf_index_filename       = data['raw_vcf_index_filename'],
              raw_vcf_id                   = data['raw_vcf_id'],
              raw_md5                      = data['raw_md5'],
              annotated_vcf_filename       = data['annotated_vcf_filename'],
              annotated_vcf_index_filename = data['annotated_vcf_index_filename'],
              annotated_vcf_id             = data['annotated_vcf_id'],
              annotated_md5                = data['annotated_md5'],
              datetime_now                 = data['datetime_now'],
              hostname                     = data['hostname'],
              docker                       = data['docker'],
              elapsed                      = data['elapsed'],
              thread_count                 = data['thread_count'])

    postgres.utils.create_table(engine, met)
    postgres.utils.add_metrics(engine, met)

class VcfState(object):
    pass

class VcfFiles(object):
    pass

def get_all_vcf_inputs(engine, inputs_table):
    '''
    Gets all the input files when the status table is not present.
    '''

    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    meta = MetaData(engine)

    #read the status table
    files = Table(inputs_table, meta,
                  Column("raw_snp_vcf_id", String, primary_key=True),
                  autoload=True)

    mapper(VcfFiles, files)

    s = [i for i in session.query(VcfFiles).all()]

    return s

def get_vcf_inputs_from_status(engine, inputs_table, status_table):
    '''
    Gets the incompleted input files when the status table is present.
    '''
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()

    meta = MetaData(engine)

    #read the status table
    state = Table(status_table, meta, autoload=True)

    mapper(VcfState, state)

    #Load all completed state data and make a dictionary
    completed = session.query(VcfState).filter(VcfState.status == 'COMPLETED').all()
    c_lst     = []
    for row in completed:
        # Key is src_vcf_id
        key = row.src_vcf_id
        c_lst.append(key)
    c_set = set(c_lst)

    # Get input table
    data = Table(inputs_table, meta,
                 Column("raw_snp_vcf_id", String, primary_key=True),
                 autoload=True)

    mapper(VcfFiles, data)

    s = []
    cases = session.query(VcfFiles).all()

    for row in cases:
        rexecute = True
        if row.raw_snp_vcf_id in c_set:
            rexecute = False

        if rexecute:
            s.append(row)

    return s
