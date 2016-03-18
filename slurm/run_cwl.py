import argparse
import pipelineUtil
import uuid
import os
import postgres
import setupLog
import logging
import tempfile
import datetime

def compress_output(workdir, logger):
    """ compress all files in a directory """


    for filename in os.listdir(workdir):
        filepath = os.path.join(workdir, filename)
        cmd = ['gzip', filepath]
        exit = pipelineUtil.run_command(cmd)
        if exit:
            raise Exception("Cannot compress file %s" %filepath)

def update_postgres(exit, cwl_failure, vcf_upload_location, snp_location ):
    """ update the status of job on postgres """

    loc = "UNKNOWN"
    status = "UNKNOWN"


    if sum(exit) == 0:

        loc = vcf_upload_location

        if not(cwl_failure):

            status = "SUCCESS"
            logger.info("uploaded all files to object store. The path is: %s" %snp_location)

        else:

            status = "COMPLETE"
            logger.info("CWL failed but outputs were generated. The path is: %s" %snp_location)

    else:

        loc = "Not Applicable"

        if not(cwl_failure):

            status = "UPLOAD FAILURE"
            logger.info("Upload of files failed")
        else:
            status = "FAILED"
            logger.info("CWL and upload both failed")
    return(status, loc)


def get_input_file(fromlocation, tolocation, logger, s3cfg="/home/ubuntu/.s3cfg"):
    """ download a file and return its location"""

    exit_code = pipelineUtil.download_from_cleversafe(logger, fromlocation, tolocation, s3cfg)

    if exit_code:
        raise Exception("Cannot download file: %s" %(fromlocation))

    outlocation = os.path.join(tolocation, os.path.basename(fromlocation))
    return outlocation

def upload_all_output(localdir, remotedir, logger, s3cfg="/home/ubuntu/.s3cfg"):
    """ upload output files to object store """

    all_exit_code = list()

    for filename in os.listdir(localdir):
        localfilepath = os.path.join(localdir, filename)
        remotefilepath = os.path.join(remotedir, filename)
        exit_code = pipelineUtil.upload_to_cleversafe(logger, remotefilepath, localfilepath, s3cfg)
        all_exit_code.append(exit_code)

    return all_exit_code


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run variant calling CWL")
    required = parser.add_argument_group("Required input parameters")
    required.add_argument("--ref", default=None, help="path to reference genome", required=True)
    required.add_argument("--normal", default=None, help="path to normal bam file", required=True)
    required.add_argument("--tumor", default=None, help="path to tumor bam file", required=True)
    required.add_argument("--normal_id", default=None, help="UUID for normal BAM", required=True)
    required.add_argument("--tumor_id", default=None, help="UUID for tumor BAM", required=True)
    required.add_argument("--case_id", default=None, help="UUID for case", required=True)
    required.add_argument("--username", default=None, help="Username for postgres", required=True)
    required.add_argument("--password", default=None, help="Password for postgres", required=True)
    required.add_argument("--refindex", default=None, help="path to reference index")
    required.add_argument("--cwl", default=None, help="Path to CWL code", required=True)

    optional = parser.add_argument_group("Optional input parameters")
    optional.add_argument("--s3dir", default="s3://bioinformatics_scratch/", help="path to output files")
    optional.add_argument("--basedir", default="/mnt/SCRATCH/", help="Base directory for computations")
    optional.add_argument("--output_vcf", default="1", help="Whether to output a VCF")
    optional.add_argument("--s3clsafe", default="/home/ubuntu/.s3cfg.cleversafe", help="config file for cleversafe")
    optional.add_argument("--s3ceph", default="/home/ubuntu/.s3cfg.ceph", help="config file for ceph")
    optional.add_argument("--host", default="pgreadwrite.osdc.io", help="hostname for postgres")

    args = parser.parse_args()

    if not os.path.isdir(args.basedir):
        raise Exception("Could not find path to base directory: %s" %args.basedir)

    #create directory structure
    casedir = tempfile.mkdtemp(prefix="%s_" %args.case_id, dir=args.basedir)
    workdir = tempfile.mkdtemp(prefix="workdir_", dir=casedir)
    inp = tempfile.mkdtemp(prefix="input_", dir=casedir)
    index = tempfile.mkdtemp(prefix="index_", dir=casedir)

    #generate a random uuid
    vcf_uuid = uuid.uuid4()
    vcf_file = "%s.vcf" %(str(vcf_uuid))

    #setup logger
    log_file = os.path.join(workdir, "%s.varscan.cwl.log" %str(vcf_uuid))
    logger = setupLog.setup_logging(logging.INFO, str(vcf_uuid), log_file)

    #logging inputs
    logger.info("normal_bam_path: %s" %(args.normal))
    logger.info("tumor_bam_path: %s" %(args.tumor))
    logger.info("normal_bam_id: %s" %(args.normal_id))
    logger.info("tumor_bam_id: %s" %(args.tumor_id))
    logger.info("case_id: %s" %(args.case_id))
    logger.info("vcf_id: %s" %(str(vcf_uuid)))

    #download reference file
    if not os.path.isfile(args.ref):
        logger.info("getting reference: %s" %args.ref)
        reference = get_input_file(args.ref, index, logger)

    #download reference index
    logger.info("Getting reference index: %s" %args.refindex)
    refindex = get_input_file(args.refindex, index, logger)

    #download normal bam
    logger.info("getting normal bam: %s" %args.normal)
    if "ceph" in args.normal:
        bam_norm = get_input_file(args.normal, inp, logger, args.s3ceph)
    else:
        bam_norm = get_input_file(args.normal, inp, logger, args.s3clsafe)

    #download tumor bam
    logger.info("getting tumor bam: %s" %args.tumor)
    if "ceph" in args.tumor:
        bam_tumor = get_input_file(args.tumor, inp, logger, args.s3ceph)
    else:
        bam_tumor = get_input_file(args.tumor, inp, logger, args.s3clsafe)

    os.chdir(workdir)

    #run cwl command
    cmd = ['/home/ubuntu/.virtualenvs/p2/bin/cwl-runner', "--debug", args.cwl,
            "--ref", reference,
            "--normal", bam_norm,
            "--tumor", bam_tumor,
            "--normal_id", args.normal_id,
            "--tumor_id", args.tumor_id,
            "--case_id", args.case_id,
            "--username", args.username,
            "--password", args.password,
            "--output_vcf", args.output_vcf,
            "--base", str(vcf_uuid),
            "--host", args.host
            ]

    cwl_exit = pipelineUtil.run_command(cmd, logger)

    #establish connection with database

    DATABASE = {
        'drivername': 'postgres',
        'host' : 'pgreadwrite.osdc.io',
        'port' : '5432',
        'username': args.username,
        'password' : args.password,
        'database' : 'prod_bioinfo'
    }

    cwl_failure= False
    engine = postgres.db_connect(DATABASE)

    #record as failure if a non-zero exit status is returned
    if cwl_exit:

        cwl_failure = True

    #upload results to s3

    snp_location = os.path.join(args.s3dir, str(vcf_uuid))
    vcf_upload_location = os.path.join(snp_location, vcf_file)

    vlog = os.path.join(workdir, "%s.varscan.log" %args.case_id)
    if os.path.isfile(vlog):
        os.rename(vlog, os.path.join(workdir, "%s.varscan.log" %str(vcf_uuid)))

    pileup = os.path.join(workdir, "%s.pileup" %args.case_id)
    if os.path.isfile(pileup):
        os.rename(pileup, os.path.join(workdir, "%s.pileup" %str(vcf_uuid)))

    compress_output(workdir, logger)
    exit = upload_all_output(workdir, snp_location, logger, args.s3ceph)

    #update postgres
    status, loc = update_postgres(exit, cwl_failure, vcf_upload_location, snp_location)
    timestamp = str(datetime.datetime.now())
    postgres.add_status(engine, args.case_id, str(vcf_uuid), [args.normal_id, args.tumor_id], status, loc, timestamp)

    #remove work and input directories
    pipelineUtil.remove_dir(casedir)
