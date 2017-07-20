"""
Main wrapper script for running the one-off workflow for processing and merging the
VarScan2 indels 
"""
import time
import argparse
import datetime
import sys

import tools.slurm
import tools.runners

import utils.pipeline

def run_tool(args):
    if args.choice == 'slurm': tools.slurm.build_slurm(args)
    elif args.choice == 'run_cwl': tools.runners.run_workflow(args)

def get_args():
    """ 
    Loads the parser
    """ 
    # Main parser
    p  = argparse.ArgumentParser(prog='varscan-indel')

    # Sub parser
    sp = p.add_subparsers(help='Choose the process you want to run', dest='choice')

    # Build slurm scripts
    p_slurm = sp.add_parser('slurm',
        help='Options for building slurm scripts. This should be the first step.')
    p_slurm.add_argument('--refdir', required=True, help='Path to the reference directory')
    p_slurm.add_argument('--config', required=True, help='Path to the postgres config file')
    p_slurm.add_argument('--slurm_thread_count', type=int,
        default=4, help='threads to consume for each job')
    p_slurm.add_argument('--mem', required=True, help='mem for each node')
    p_slurm.add_argument('--outdir', default="./",
        help='output directory for slurm scripts [./]')
    p_slurm.add_argument('--output_s3dir', required=True, help='s3bin for output files')
    p_slurm.add_argument('--run_basedir', default="/mnt/SCRATCH", help='basedir for cwl runs')
    p_slurm.add_argument('--log_file', type=str,
        help='If you want to write the logs to a file. By default stdout')
    p_slurm.add_argument('--input_table_id', type=str, 
        default='varscan_indel_recover_20170629_input',
        help='postgres input table [varscan_indel_recover_20170629_input]')
    p_slurm.add_argument('--status_table_id', type=str, 
        default='varscan_indel_recover_20170629_cwl_status',
        help='postgres status table [varscan_indel_recover_20170629_cwl_status]')
    p_slurm.add_argument('--partition', type=str, required=False, help='slurm partition id')

    # Run cwl
    p_cwl = sp.add_parser('run_cwl', help='Options for running the CWL workflows')
    p_cwl.add_argument('--refdir', required=True, help='Path to the reference directory')
    p_cwl.add_argument('--basedir', required=True, help='Working directory')
    p_cwl.add_argument('--thread_count', type=int, default=4,
        help='number of threads to use for VEP') 
    p_cwl.add_argument('--input_bam', type=str, required=True,
        help='s3 path to tumor bam')
    p_cwl.add_argument('--input_bam_index', type=str, required=True,
        help='s3 path to tumor bam index')
    p_cwl.add_argument('--program', type=str, required=True, help='Program ID')
    p_cwl.add_argument('--project', type=str, required=True, help='Project ID')
    p_cwl.add_argument('--case_id', type=str, required=True, help='Case ID')
    p_cwl.add_argument('--src_vcf_id', type=str, required=True, help='Source VCF UUID')
    p_cwl.add_argument('--tumor_bam_uuid', type=str, required=True, help='Tumor BAM UUID')
    p_cwl.add_argument('--normal_bam_uuid', type=str, required=True, help='Normal BAM UUID')
    p_cwl.add_argument('--s3dir', type=str, required=True, help='S3 path to upload to')
    p_cwl.add_argument('--hc_snp_vcf', type=str, required=True, help='S3 location of HC SNP VCF')
    p_cwl.add_argument('--biasfiltered_vcf', type=str, required=True, 
        help='S3 location of bias filtered VCF')
    p_cwl.add_argument('--raw_indel_vcf', type=str, required=True, 
        help='S3 location of the raw indel VCF')
    p_cwl.add_argument('--python', type=str, required=True,
        help='path to python executable')
    p_cwl.add_argument('--script', type=str, required=True,
        help='path to ProcessSnpVcf.py')
    p_cwl.add_argument('--cwl', type=str, required=True,
        help='path to workflow CWL')
    p_cwl.add_argument('--no_cleanup', action='store_true',
        help='for debug dont cleanup files')

    return p.parse_args()

if __name__ == '__main__':
    start = time.time()

    # Set up logger
    logger    = utils.pipeline.setup_logging('varscan_indel')

    # Print header
    logger.info('-'*75)
    logger.info('varscan-indel-oneoff-workflow.py')
    logger.info("Program Args: varscan-indel-oneoff-workflow.py " + " ".join(sys.argv[1::]))
    logger.info('Date/time: {0}'.format(datetime.datetime.now()))
    logger.info('-'*75)
    logger.info('-'*75)

    # Get args
    args = get_args()

    # Run tool
    run_tool(args)

    # Done
    logger.info("Finished, took {0} seconds.".format(
                time.time() - start))
