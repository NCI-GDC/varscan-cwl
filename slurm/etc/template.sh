#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task={SLURM_THREAD_COUNT}
#SBATCH --ntasks=1
#SBATCH --workdir={BASEDIR}
#SBATCH --mem={MEM}
{PARTITION}

# IDS
program="{PROGRAM}"
project="{PROJECT}"
case_id="{CASE_ID}"
tumor_bam_uuid="{TUMOR_BAM_UUID}"
normal_bam_uuid="{NORMAL_BAM_UUID}"
src_vcf_id="{SRC_VCF_ID}"

# Input
input_bam="{INPUT_BAM}"
input_bai="{INPUT_BAI}"
input_hc_snp_vcf="{HC_SNP_VCF}"
input_biasfiltered_vcf="{BIAS_VCF}"
input_raw_indel_vcf="{RAW_INDEL_VCF}"

# Reference DB
refdir="{REFDIR}"

# Outputs
s3dir="{S3DIR}"
basedir="{BASEDIR}"
repository="git@github.com:NCI-GDC/varscan-cwl.git"
wkdir=`sudo mktemp -d varscan_indel.XXXXXXXXXX -p $basedir`
sudo chown ubuntu:ubuntu $wkdir

cd $wkdir

function cleanup (){{
    echo "cleanup tmp data";
    sudo rm -rf $wkdir;
}}

sudo git clone -b fix/indel-oneoff $repository
sudo chown ubuntu:ubuntu -R varscan-cwl 

trap cleanup EXIT

/home/ubuntu/.virtualenvs/p2/bin/python varscan-cwl/slurm/varscan-indel-oneoff-workflow.py run_cwl \
--basedir $wkdir \
--refdir $refdir \
--input_bam $input_bam \
--thread_count {SLURM_THREAD_COUNT} \
--input_bam_index $input_bai \
--program $program \
--project $project \
--case_id $case_id \
--tumor_bam_uuid $tumor_bam_uuid \
--normal_bam_uuid $normal_bam_uuid \
--s3dir $s3dir \
--hc_snp_vcf $input_hc_snp_vcf \
--biasfiltered_vcf $input_biasfiltered_vcf \
--raw_indel_vcf $input_raw_indel_vcf \
--src_vcf_id $src_vcf_id \
--python /home/ubuntu/.virtualenvs/p2/bin/python \
--script $wkdir/varscan-cwl/scripts/ProcessSnpVcf.py \
--cwl $wkdir/varscan-cwl/workflows/varscan_indel_oneoff.workflow.cwl
