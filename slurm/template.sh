#!/bin/bash
#SBATCH --nodes=1
#SBATCH --cpus-per-task=40
#SBATCH --workdir=/mnt/SCRATCH/

normal="XX_NORMAL_XX"
tumor="XX_TUMOR_XX"
normal_id="XX_NORMAL_ID_XX"
tumor_id="XX_TUMOR_ID_XX"
case_id="XX_CASE_ID_XX"
basedir="/mnt/SCRATCH/"
ref="s3://bioinformatics_scratch/GRCh38.d1.vd1.fa"
refindex="s3://bioinformatics_scratch/GRCh38.d1.vd1.fa.fai"
username="username"
password="password"
repository="git@github.com:NCI-GDC/varscan-cwl.git"
cwl="/home/ubuntu/varscan-cwl/tools/varscan-tool.cwl.yaml"
dir="/home/ubuntu/varscan-cwl/"

if [ ! -d $dir ];then
    sudo git clone -b feat/slurm $repository $dir 
    sudo chown ubuntu:ubuntu $dir
fi

/home/ubuntu/.virtualenvs/p2/bin/python /home/ubuntu/somaticsniper-cwl/slurm/run_cwl.py --ref $ref --refindex $refindex --normal $normal --tumor $tumor --normal_id $normal_id --tumor_id $tumor_id --case_id $case_id --username $username --password $password --basedir $basedir --cwl $cwl
