"""Module for running the CWL workflow"""
import json
import os
import uuid
import socket
import time
import tempfile
import logging

import utils.pipeline
from tools.varscan_indel_oneoff import VarscanIndelOneoffTool

def run_workflow(args):
    """
    Main wrapper for running workflow.
    """
    if not os.path.isdir(args.basedir):
        try: os.makedirs(args.basedir)
        except: raise Exception("Could not find path to base directory: {0}".format(args.basedir))


    # Extract metadata
    project       = args.project
    program       = args.program
    case_id       = args.case_id
    src_vcf_id    = args.src_vcf_id
    tumor_bam_id  = args.tumor_bam_uuid
    normal_bam_id = args.normal_bam_uuid

    # Generate UUIDs
    raw_vcf_uuid       = str(uuid.uuid4()) 
    annotated_vcf_uuid = str(uuid.uuid4()) 

    #create directory structure
    uniqdir  = tempfile.mkdtemp(prefix="varscan_indel_%s_" % str(raw_vcf_uuid),
                                dir=args.basedir)
    workdir  = tempfile.mkdtemp(prefix="workdir_", dir=uniqdir)
    inputdir = tempfile.mkdtemp(prefix="input_", dir=uniqdir)

    # get hostname
    hostname = socket.gethostname()

    # setup logging
    log_file = os.path.join(workdir, '{0}.varscan_indel_oneoff.cwl.log'.format(raw_vcf_uuid))
    logger   = utils.pipeline.setup_logging(raw_vcf_uuid, log_file)

    # Logging inputs
    logger.info("hostname: {0}".format(hostname))
    logger.info("raw_vcf_uuid: {0}".format(raw_vcf_uuid))
    logger.info("annotated_vcf_uuid: {0}".format(annotated_vcf_uuid))
    logger.info("program: {0}".format(program))
    logger.info("project: {0}".format(project))
    logger.info("case_id: {0}".format(case_id))
    logger.info("src_vcf_id: {0}".format(src_vcf_id))

    # load resource
    resource_json = os.path.join(os.path.realpath(os.path.dirname(os.path.dirname(__file__))), 
        'resources/varscan_indel_oneoff.resources.json')

    # run tool
    try:
        tool = VarscanIndelOneoffTool(
          workdir            = workdir,
          inputdir           = inputdir, 
          refdir             = args.refdir,
          resource_json_file = resource_json,
          hostname           = hostname,
          program            = program,
          project            = project,
          case_id            = case_id,
          src_vcf_id         = src_vcf_id,
          tumor_bam_id       = tumor_bam_id,
          normal_bam_id      = normal_bam_id,
          raw_vcf_id         = raw_vcf_uuid,
          annotated_vcf_id   = annotated_vcf_uuid,
          hc_snp_vcf         = args.hc_snp_vcf,
          raw_indel_vcf      = args.raw_indel_vcf,
          biasfiltered_vcf   = args.biasfiltered_vcf,
          tumor_bam          = args.input_bam,
          tumor_index        = args.input_bam_index,
          python_exe         = args.python,
          script_path        = args.script,
          s3dir              = args.s3dir,
          threads            = args.thread_count,
          logger             = logger,
          cwl_tool           = args.cwl,
          no_cleanup         = args.no_cleanup
        )
        tool.run()
    finally:
        if not args.no_cleanup:
            utils.pipeline.remove_dir(uniqdir) 
