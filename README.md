# GDC VarScan2 CWL
![Version badge](https://img.shields.io/badge/VarScan-v2.3.9-<COLOR>.svg)

VarScan is a platform-independent mutation caller for targeted, exome, and whole-genome resequencing data generated on Illumina, SOLiD, Life/PGM, Roche/454, and similar instruments. The VarScan2 can be used to detect different types of variation:
*   Germline variants (SNPs an dindels) in individual samples or pools of samples.
*   Multi-sample variants (shared or private) in multi-sample datasets (with mpileup).
*   Somatic mutations, LOH events, and germline variants in tumor-normal pairs.
*   Somatic copy number alterations (CNAs) in tumor-normal exome data.

Original VarScan2: http://dkoboldt.github.io/varscan/

## Docker

All the docker images are built from `Dockerfile`s at https://github.com/NCI-GDC/varscan-tool.

## CWL

https://www.commonwl.org/

The CWL are tested under multiple `cwltools` environments. The most tested one is:
* cwltool 1.0.20180306163216


## For external users

There is a production-ready GDC CWL workflow at https://github.com/NCI-GDC/gdc-somatic-variant-calling-workflow, which uses this repo as a git submodule.

Please notice that you may want to change the docker image host of `dockerPull:` for each CWL.

To use CWL directly from this repo, we recommend to run
* `tools/multi_varscan2.cwl` on an array of tumor/normal mpileup files with tumor/normal bam files.

To run CWL:

```
>>>>>>>>>>Multi VarScan2<<<<<<<<<<
cwltool tools/multi_varscan2.cwl -h
/home/ubuntu/.virtualenvs/p2/bin/cwltool 1.0.20180306163216
Resolved 'tools/multi_varscan2.cwl' to 'file:///mnt/SCRATCH/githubs/submodules/v/varscan-cwl/tools/multi_varscan2.cwl'
usage: tools/multi_varscan2.cwl [-h] [--java_opts JAVA_OPTS]
                                [--max_normal_freq MAX_NORMAL_FREQ]
                                [--min_cov_normal MIN_COV_NORMAL]
                                [--min_cov_tumor MIN_COV_TUMOR]
                                [--min_coverage MIN_COVERAGE]
                                [--min_freq_for_hom MIN_FREQ_FOR_HOM]
                                [--min_tumor_freq MIN_TUMOR_FREQ]
                                [--min_var_freq MIN_VAR_FREQ]
                                [--normal_purity NORMAL_PURITY] --output_vcf
                                OUTPUT_VCF --ref_dict REF_DICT
                                [--somatic_p_value SOMATIC_P_VALUE]
                                --strand_filter STRAND_FILTER --thread_count
                                THREAD_COUNT --tn_pair_pileup TN_PAIR_PILEUP
                                [--tumor_purity TUMOR_PURITY] --validation
                                [--vps_p_value VPS_P_VALUE]
                                [--vs_p_value VS_P_VALUE]
                                [job_order]

positional arguments:
  job_order             Job input json file

optional arguments:
  -h, --help            show this help message and exit
  --java_opts JAVA_OPTS
                        "JVM arguments should be a quoted, space separated
                        list (e.g. -Xmx8g -Xmx16g -Xms128m -Xmx512m)"
  --max_normal_freq MAX_NORMAL_FREQ
                        Maximum variant allele frequency in normal [0.05]
  --min_cov_normal MIN_COV_NORMAL
                        Minimum coverage in normal to call somatic (8)
  --min_cov_tumor MIN_COV_TUMOR
                        Minimum coverage in tumor to call somatic (6)
  --min_coverage MIN_COVERAGE
                        Minimum coverage in normal and tumor to call variant
                        (8)
  --min_freq_for_hom MIN_FREQ_FOR_HOM
                        Minimum frequency to call homozygote (0.75)
  --min_tumor_freq MIN_TUMOR_FREQ
                        Minimun variant allele frequency in tumor [0.10]
  --min_var_freq MIN_VAR_FREQ
                        Minimum variant frequency to call a heterozygote
                        (0.10)
  --normal_purity NORMAL_PURITY
                        Estimated purity (non-tumor content) of normal sample
                        (1.00)
  --output_vcf OUTPUT_VCF
                        If set to 1, output VCF instead of VarScan native
                        format
  --ref_dict REF_DICT   reference sequence dictionary file
  --somatic_p_value SOMATIC_P_VALUE
                        P-value threshold to call a somatic site (0.05)
  --strand_filter STRAND_FILTER
                        If set to 1, removes variants with >90% strand bias
                        (0)
  --thread_count THREAD_COUNT
  --tn_pair_pileup TN_PAIR_PILEUP
                        The SAMtools pileup file for tumor/normal pair
  --tumor_purity TUMOR_PURITY
                        Estimated purity (tumor content) of tumor sample
                        (1.00)
  --validation          If set, outputs all compared positions even if non-
                        variant
  --vps_p_value VPS_P_VALUE
                        P-value for high-confidence calling [0.07]
  --vs_p_value VS_P_VALUE
                        P-value threshold to call a heterozygote (0.99)
```

## For GDC users

See https://github.com/NCI-GDC/gdc-somatic-variant-calling-workflow.
