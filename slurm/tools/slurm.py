"""Module to build the slurm scripts for the varscan indel
workflow.
"""
import os
from sqlalchemy.exc import NoSuchTableError

import utils.pipeline

import postgres.vcf_status
import postgres.utils
#prod_bioinfo-> \d varscan_indel_recover_20170629_input
#     Table "public.varscan_indel_recover_20170629_input"
#           Column            |       Type        | Modifiers
#-----------------------------+-------------------+-----------
# program                     | text              |
# project                     | text              |
# patient_barcode             | text              |
# case_id                     | uuid              |
# normal_barcode              | text              |
# normal_aliquot_id           | uuid              |
# normal_cghub_id             | text              |
# normal_bam_uuid             | text              |
# normal_bam_location         | text              |
# tumor_barcode               | text              |
# tumor_aliquot_id            | uuid              |
# tumor_cghub_id              | text              |
# tumor_bam_uuid              | text              |
# tumor_bam_location          | text              |
# center                      | text              |
# sequencer                   | text              |
# raw_snp_vcf_id              | character varying |
# raw_snp_vcf_location        | character varying |
# fpfilter_snp_vcf_id         | text              |
# fpfilter_snp_vcf_location   | text              |
# annotated_snp_vcf_id        | character varying |
# annotated_snp_vcf_location  | character varying |
# biasfilter_snp_vcf_id       | character varying |
# biasfilter_snp_vcf_location | text              |
# raw_indel_vcf_location      | text              |

def build_slurm(args):
    """
    Builds the slurm script for the varscan indel workflow.
    """
    logger = utils.pipeline.setup_logging("slurm")
    logger.info("Running build slurm for VarScan2 InDel workflows")

    # Check paths
    if not os.path.isdir(args.outdir):
        try: os.makedirs(args.outdir)
        except: 
            logger.error("Unable to create output directory: {0}".format(args.outdir))
            raise Exception()

    if not os.path.isfile(args.config):
        logger.error("Cannot find config file: {0}".format(args.config))
        raise Exception() 

    # Database setup
    engine = postgres.utils.get_db_engine(args.config)

    try:
        results = postgres.vcf_status.get_vcf_inputs_from_status(
            engine,
            args.input_table_id,
            args.status_table_id
        )
    except NoSuchTableError:
        results = postgres.vcf_status.get_all_vcf_inputs(
            engine,
            args.input_table_id
        )

    template = _load_template()

    for result in results:
        bam  = result.tumor_bam_location
        bai  = os.path.splitext(bam)[0] + '.bai'
        cid  = result.raw_snp_vcf_id
        ofil = os.path.join(args.outdir, "varscan_indels.{0}.sh".format(cid))
        curr = template.format(
            PROGRAM=result.program,
            PROJECT=result.project,
            CASE_ID=result.case_id,
            INPUT_BAM=bam,
            INPUT_BAI=bai,
            TUMOR_BAM_UUID=result.tumor_bam_uuid,
            NORMAL_BAM_UUID=result.normal_bam_uuid,
            SLURM_THREAD_COUNT=args.slurm_thread_count,
            MEM=args.mem,
            BASEDIR=args.run_basedir,
            SRC_VCF_ID=cid,
            HC_SNP_VCF=result.raw_snp_vcf_location,
            BIAS_VCF=result.biasfilter_snp_vcf_location,
            S3DIR=args.output_s3dir,
            REFDIR=args.refdir,
            RAW_INDEL_VCF=result.raw_indel_vcf_location,
            PARTITION="#SBATCH --partition={0}".format(args.partition) if args.partition else ""
        )
        with open(ofil, 'wt') as o:
            o.write(curr)

def _load_template():
    pth = os.path.realpath(os.path.dirname(os.path.dirname(__file__)))
    tfil = os.path.join(pth, 'etc/template.sh')
    dat = None
    with open(tfil, 'rt') as fh:
        dat = fh.read()
    return dat 
