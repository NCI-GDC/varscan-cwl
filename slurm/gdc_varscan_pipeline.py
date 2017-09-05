'''
Main wrapper script for VarScan (v2.3.9) pipeline
'''
import os
import time
import argparse
import logging
import sys
import uuid
import tempfile
import utils.s3
import utils.pipeline
import datetime
import socket
import json
import postgres.status
import postgres.utils
import postgres.mixins
import glob
from sqlalchemy.exc import NoSuchTableError

def is_nat(x):
    '''
    Checks that a value is a natural number.
    '''
    if int(x) > 0:
        return int(x)
    raise argparse.ArgumentTypeError('%s must be positive, non-zero' % x)

def get_args():
    '''
    Loads the parser
    '''
    # Main parser
    parser = argparse.ArgumentParser(description="VarScan (v2.3.9) Pipeline")
    # Args
    required = parser.add_argument_group("Required input parameters")
    # Metadata from input table
    required.add_argument("--case_id", default=None, help="Case ID, internal production id.")
    required.add_argument("--tumor_gdc_id", default=None, help="Tumor GDC ID, GDC portal id.")
    required.add_argument("--tumor_s3_url", default=None, help="S3_URL, s3 url of the tumor input.")
    required.add_argument("--t_s3_profile", required=True, help="S3 profile name for project tenant.")
    required.add_argument("--t_s3_endpoint", required=True, help="S3 endpoint url for project tenant.")
    required.add_argument("--normal_gdc_id", default=None, help="Normal GDC ID, GDC portal id.")
    required.add_argument("--normal_s3_url", default=None, help="S3_URL, s3 url of the normal input.")
    required.add_argument("--n_s3_profile", required=True, help="S3 profile name for project tenant.")
    required.add_argument("--n_s3_endpoint", required=True, help="S3 endpoint url for project tenant.")
    # Parameters for pipeline
    required.add_argument("--basedir", default="/mnt/SCRATCH/", help="Base directory for computations.")
    required.add_argument("--refdir", required=True, help="Path to reference directory.")
    required.add_argument("--workflow_cwl", required=True, help="Path to CWL workflow.")
    required.add_argument("--index_cwl", required=True, help="Path to Picard buildbamindex CWL tool.")
    required.add_argument("--sort_cwl", required=True, help="Path to Picard sortvcf CWL tool.")
    required.add_argument("--s3dir", default="s3://", help="S3bin for uploading output files.")
    required.add_argument("--s3_profile", required=True, help="S3 profile name for project tenant.")
    required.add_argument("--s3_endpoint", required=True, help="S3 endpoint url for project tenant.")
    # Parameters for parallelization
    required.add_argument("--block", type=is_nat, default=30000000, help="Parallel block size.")
    required.add_argument('--thread_count', type=is_nat, default=8, help='Threads count.')

    return parser.parse_args()

def run_pipeline(args, statusclass, metricsclass):
    '''
    Executes the CWL pipeline and record status/metrics tables
    '''
    if not os.path.isdir(args.basedir):
        raise Exception("Could not find path to base directory: %s" %args.basedir)
    # Generate a uuid
    output_id = str(uuid.uuid4())
    hostname = socket.gethostname()
    # Get datetime start
    datetime_start = str(datetime.datetime.now())
    # Create directory structure
    jobdir = tempfile.mkdtemp(prefix="{0}_{1}_".format("varscan", str(output_id)), dir=args.basedir)
    workdir = tempfile.mkdtemp(prefix="workdir_", dir=jobdir)
    inputdir = tempfile.mkdtemp(prefix="input_", dir=jobdir)
    resultdir = tempfile.mkdtemp(prefix="result_", dir=jobdir)
    jsondir = tempfile.mkdtemp(prefix="input_json_", dir=workdir)
    refdir = args.refdir
    # Setup logger
    log_file = os.path.join(resultdir, "{0}.{1}.cwl.log".format("varscan", str(output_id)))
    logger = utils.pipeline.setup_logging(logging.INFO, str(output_id), log_file)
    # Logging inputs
    logger.info("pipeline: varscan")
    logger.info("hostname: {}".format(hostname))
    logger.info("case_id: {}".format(args.case_id))
    logger.info("tumor_gdc_id: {}".format(args.tumor_gdc_id))
    logger.info("normal_gdc_id: {}".format(args.normal_gdc_id))
    logger.info("datetime_start: {}".format(datetime_start))
    # Setup start point
    cwl_start = time.time()
    # Getting refs
    logger.info("getting resources")
    reference_data        = utils.pipeline.load_reference_json()
    reference_fasta_path  = os.path.join(refdir, reference_data["reference_fasta"])
    reference_fasta_fai   = os.path.join(refdir, reference_data["reference_fasta_index"])
    reference_fasta_dict  = os.path.join(refdir, reference_data["reference_fasta_dict"])
    java_opts             = reference_data["java_opts"]
    min_coverage          = reference_data["min_coverage"]
    min_cov_normal        = reference_data["min_cov_normal"]
    min_cov_tumor         = reference_data["min_cov_tumor"]
    min_var_freq          = reference_data["min_var_freq"]
    min_freq_for_hom      = reference_data["min_freq_for_hom"]
    normal_purity         = reference_data["normal_purity"]
    tumor_purity          = reference_data["tumor_purity"]
    vs_p_value            = reference_data["vs_p_value"]
    somatic_p_value       = reference_data["somatic_p_value"]
    is_vcf                = reference_data["output_vcf"]
    min_tumor_freq        = reference_data["min_tumor_freq"]
    max_normal_freq       = reference_data["max_normal_freq"]
    vps_p_value           = reference_data["vps_p_value"]
    postgres_config       = os.path.join(refdir, reference_data["pg_config"])
    # Logging pipeline info
    cwl_version    = reference_data["cwl_version"]
    docker_version = reference_data["docker_version"]
    logger.info("cwl_version: {}".format(cwl_version))
    logger.info("docker_version: {}".format(docker_version))
    # Download input
    normal_bam = os.path.join(inputdir, os.path.basename(args.normal_s3_url))
    normal_download_cmd = " ".join(utils.s3.aws_s3_get(logger, args.normal_s3_url, inputdir,
                                             args.n_s3_profile, args.n_s3_endpoint, recursive=False))
    tumor_bam = os.path.join(inputdir, os.path.basename(args.tumor_s3_url))
    tumor_download_cmd = " ".join(utils.s3.aws_s3_get(logger, args.tumor_s3_url, inputdir,
                                             args.t_s3_profile, args.t_s3_endpoint, recursive=False))
    download_cmd = [normal_download_cmd, tumor_download_cmd]
    download_exit = utils.pipeline.multi_commands(download_cmd, 2, logger)
    download_end_time = time.time()
    download_time = download_end_time - cwl_start
    if any(x != 0 for x in download_exit):
        cwl_elapsed = download_time
        datetime_end = str(datetime.datetime.now())
        engine = postgres.utils.get_db_engine(postgres_config)
        download_exit_code = next((x for x in download_exit if x != 0), None)
        postgres.utils.set_download_error(download_exit_code, logger, engine,
                                          args.case_id, args.tumor_gdc_id, args.normal_gdc_id, output_id,
                                          datetime_start, datetime_end,
                                          hostname, cwl_version, docker_version,
                                          download_time, cwl_elapsed, statusclass, metricsclass)
        # Exit
        sys.exit(download_exit_code)
    else:
        logger.info("Download successfully. Normal bam is %s, and tumor bam is %s." % (normal_bam, tumor_bam))
    # Pull docker images
    docker_pull_cmd_list = []
    for image in docker_version:
        cmd = utils.pipeline.docker_pull_cmd(image)
        docker_pull_cmd_list.append(cmd)
    docker_pull_exit = utils.pipeline.multi_commands(docker_pull_cmd_list, len(docker_pull_cmd_list), logger)
    if any(x != 0 for x in docker_pull_exit):
        logger.info("Failed to pull docker images.")
        docker_pull_exit_code = next((x for x in index_exit if x != 0), None)
        sys.exit(docker_pull_exit_code)
    else:
        logger.info("Pulled all docker images. {}".format(docker_version))
    # Build index
    normal_bam_index_cmd = utils.pipeline.get_index_cmd(inputdir, args.index_cwl, normal_bam)
    tumor_bam_index_cmd = utils.pipeline.get_index_cmd(inputdir, args.index_cwl, tumor_bam)
    index_cmd = [normal_bam_index_cmd, tumor_bam_index_cmd]
    os.chdir(inputdir)
    index_exit = utils.pipeline.multi_commands(index_cmd, 2, logger)
    if any(x != 0 for x in index_exit):
        logger.info("Failed to build bam index.")
        index_exit_code = next((x for x in index_exit if x != 0), None)
        sys.exit(index_exit_code)
    else:
        logger.info("Build {}, {} index successfully".format(os.path.basename(normal_bam), os.path.basename(tumor_bam)))
    # Create input json
    os.chdir(workdir)
    input_json_list = []
    for i, block in enumerate(utils.pipeline.fai_chunk(reference_fasta_fai, args.block)):
        input_json_file = os.path.join(jsondir, '{0}.{4}.{1}.{2}.{3}.varscan.inputs.json'.format(str(output_id), block[0], block[1], block[2], i))
        input_json_data = {
          "ref": {"class": "File", "path": reference_fasta_path},
          "region": "{}:{}-{}".format(block[0], block[1], block[2]),
          "normal_bam": {"class": "File", "path": normal_bam},
          "tumor_bam": {"class": "File", "path": tumor_bam},
          "prefix": "{}_{}_{}".format(block[0], block[1], block[2]),
          "java_opts": java_opts,
          "min_coverage": min_coverage,
          "min_cov_normal": min_cov_normal,
          "min_cov_tumor": min_cov_tumor,
          "min_var_freq": min_var_freq,
          "min_freq_for_hom": min_freq_for_hom,
          "normal_purity": normal_purity,
          "tumor_purity": tumor_purity,
          "vs_p_value": vs_p_value,
          "somatic_p_value": somatic_p_value,
          "output_vcf": is_vcf,
          "min_tumor_freq": min_tumor_freq,
          "max_normal_freq": max_normal_freq,
          "vps_p_value": vps_p_value,
          "ref_dict": {"class": "File", "path": reference_fasta_dict}
        }
        with open(input_json_file, 'wt') as o:
            json.dump(input_json_data, o, indent=4)
        input_json_list.append(input_json_file)
    logger.info("Preparing input json")
    # Run CWL
    logger.info('Running CWL workflow')
    cmds = list(utils.pipeline.cmd_template(inputdir = inputdir, workdir = workdir, cwl_path = args.workflow_cwl, input_json = input_json_list))
    cwl_exit = utils.pipeline.multi_commands(cmds, args.thread_count, logger)
    # Create sort json
    merged_vcf_list = glob.glob(os.path.join(workdir, "*.merged.vcf"))
    merged_sort_json = utils.pipeline.create_sort_json(reference_fasta_dict, str(output_id), "snp.indel.hc.updated.merged", jsondir, workdir, merged_vcf_list, logger)
    # Run Sort
    merged_sort_cmd = ['/home/ubuntu/.virtualenvs/p2/bin/cwltool',
                      "--debug",
                      "--tmpdir-prefix", inputdir,
                      "--tmp-outdir-prefix", workdir,
                      args.sort_cwl,
                      merged_sort_json]
    merged_exit = utils.pipeline.run_command(merged_sort_cmd, logger)
    cwl_exit.append(merged_exit)
    # Compress the outputs and CWL logs
    os.chdir(jobdir)
    output_vcf = "{0}.{1}.vcf.gz".format(str(output_id), "snp.indel.hc.updated.merged")
    output_tar = os.path.join(resultdir, "%s.%s.tar.bz2" % ("varscan", str(output_id)))
    logger.info("Compressing workflow outputs: %s" % (output_tar))
    utils.pipeline.targz_compress(logger, output_tar, os.path.basename(workdir), cmd_prefix=['tar', '-cjvf'])
    output_vcf_path = os.path.join(resultdir, output_vcf)
    os.rename(os.path.join(workdir, output_vcf), output_vcf_path)
    os.rename(os.path.join(workdir, output_vcf + ".tbi"), os.path.join(resultdir, output_vcf + ".tbi"))
    upload_dir_location = os.path.join(args.s3dir, str(output_id))
    upload_file_location = os.path.join(upload_dir_location, output_vcf)
    # Get md5 and file size
    md5 = utils.pipeline.get_md5(output_vcf_path)
    file_size = utils.pipeline.get_file_size(output_vcf_path)
    # Upload output
    upload_start = time.time()
    logger.info("Uploading workflow output to %s" % (upload_file_location))
    upload_exit  = utils.s3.aws_s3_put(logger, upload_dir_location, resultdir, args.s3_profile, args.s3_endpoint, recursive=True)
    # Establish connection with database
    engine = postgres.utils.get_db_engine(postgres_config)
    # End time
    cwl_end = time.time()
    upload_time = cwl_end - upload_start
    cwl_elapsed = cwl_end - cwl_start
    datetime_end = str(datetime.datetime.now())
    logger.info("datetime_end: %s" % (datetime_end))
    # Get status info
    logger.info("Get status/metrics info")
    status, loc = postgres.status.get_status(upload_exit, cwl_exit, upload_file_location, upload_dir_location, logger)
    # Get metrics info
    time_metrics = utils.pipeline.get_time_metrics(log_file)
    # Set status table
    logger.info("Updating status")
    postgres.utils.add_pipeline_status(engine, args.case_id, args.tumor_gdc_id, args.normal_gdc_id, output_id,
                                       status, loc, datetime_start, datetime_end,
                                       md5, file_size, hostname, cwl_version, docker_version, statusclass)
    # Set metrics table
    logger.info("Updating metrics")
    postgres.utils.add_pipeline_metrics(engine, args.case_id, args.tumor_gdc_id, args.normal_gdc_id, download_time,
                                        upload_time, str(args.thread_count), cwl_elapsed,
                                        sum(time_metrics['system_time'])/float(len(time_metrics['system_time'])),
                                        sum(time_metrics['user_time'])/float(len(time_metrics['user_time'])),
                                        sum(time_metrics['wall_clock'])/float(len(time_metrics['wall_clock'])),
                                        sum(time_metrics['percent_of_cpu'])/float(len(time_metrics['percent_of_cpu'])),
                                        sum(time_metrics['maximum_resident_set_size'])/float(len(time_metrics['maximum_resident_set_size'])),
                                        status, metricsclass)
    # Remove job directories, upload final log file
    logger.info("Uploading main log file")
    utils.s3.aws_s3_put(logger, upload_dir_location + '/' + os.path.basename(log_file), log_file, args.s3_profile, args.s3_endpoint, recursive=False)
    utils.pipeline.remove_dir(jobdir)

if __name__ == '__main__':
    # Get args
    args = get_args()
    # Setup postgres classes
    class VarScanStatus(postgres.mixins.StatusTypeMixin, postgres.utils.Base):
        __tablename__ = 'varscan_vc_cwl_status'
    class VarScanMetrics(postgres.mixins.MetricsTypeMixin, postgres.utils.Base):
        __tablename__ = 'varscan_vc_cwl_metrics'
    # Run pipeline
    run_pipeline(args, VarScanStatus, VarScanMetrics)
