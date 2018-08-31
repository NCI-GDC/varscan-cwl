'''
Postgres tables for the PDC CWL Workflow
'''
import postgres.utils
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, mapper
from sqlalchemy import MetaData, Table
from sqlalchemy import Column, String

def get_status(upload_exit, cwl_exit, upload_file_location, upload_dir_location, logger):
    """ update the status of job on postgres """
    loc = 'UNKNOWN'
    status = 'UNKNOWN'
    if upload_exit == 0:
        loc = upload_file_location
        if any(x != 0 for x in cwl_exit):
            status = 'CWL_FAILED'
            logger.info("CWL failed. The log path is: %s" % upload_dir_location)
        else:
            status = 'COMPLETED'
            logger.info("uploaded all files to object store. The path is: %s" % upload_dir_location)
    else:
        loc = 'Not Applicable'
        if any(x != 0 for x in cwl_exit):
            status = 'FAILED'
            logger.info("CWL and upload both failed")
        else:
            status = 'UPLOAD_FAILURE'
            logger.info("Upload of files failed")
    return(status, loc)

class State(object):
    pass

class Files(object):
    pass

def get_case(engine, input_table, status_table, input_primary_column="id"):
    Session = sessionmaker()
    Session.configure(bind=engine)
    session = Session()
    meta = MetaData(engine)
    #read the input table
    data = Table(input_table, meta, Column(input_primary_column, String, primary_key=True), autoload=True)
    mapper(Files, data)
    count = 0
    s = dict()
    cases = session.query(Files).all()
    if status_table == "None":
        for row in cases:
            s[count] = [row.case_id,
                        row.tumor_gdc_id,
                        row.normal_gdc_id,
                        row.tumor_s3_url,
                        row.normal_s3_url]
            count += 1
    else:
        #read the status table
        state = Table(status_table, meta, autoload=True)
        mapper(State, state)
        completed = session.query(State).filter(State.status == 'COMPLETED').all()
        for row in cases:
            if (row.tumor_gdc_id, row.normal_gdc_id) not in (completed.tumor_gdc_id, completed.normal_gdc_id):
                s[count] = [row.case_id,
                            row.tumor_gdc_id,
                            row.normal_gdc_id,
                            row.tumor_s3_url,
                            row.normal_s3_url]
                count += 1
    return s
