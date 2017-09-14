#!/usr/bin/env cwl-runner

cwlVersion: v1.0

doc: |
    Run VarScan.v2.3.9 pipeline

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: SubworkflowFeatureRequirement
  - class: ScatterFeatureRequirement

class: Workflow

inputs:
  - id: ref
    doc: Reference sequence for SAMtools mpileup
    type: File
  - id: region
    doc: Chromosome region for SAMtools mpileup
    type: string
  - id: normal_bam
    doc: Normal bam file
    type: File
  - id: tumor_bam
    doc: Tumor bam file
    type: File
  - id: prefix
    doc: Prefix for all the outputs
    type: string
  - id: min_MQ
    doc: skip alignments with mapQ smaller than INT [0]
    type: int
    default: 1
  - id: java_opts
    doc: Java option flags for all the java cmd
    type: string
    default: '3G'
  - id: min_coverage
    doc: Minimum coverage in normal and tumor to call variant (8)
    type: int
    default: 8
  - id: min_cov_normal
    doc: Minimum coverage in normal to call somatic (8)
    type: int
    default: 8
  - id: min_cov_tumor
    doc: Minimum coverage in tumor to call somatic (6)
    type: int
    default: 6
  - id: min_var_freq
    doc: Minimum variant frequency to call a heterozygote (0.10)
    type: float
    default: 0.10
  - id: min_freq_for_hom
    doc: Minimum frequency to call homozygote (0.75)
    type: float
    default: 0.75
  - id: normal_purity
    doc: Estimated purity (non-tumor content) of normal sample (1.00)
    type: float
    default: 1.00
  - id: tumor_purity
    doc: Estimated purity (tumor content) of tumor sample (1.00)
    type: float
    default: 1.00
  - id: vs_p_value
    doc: P-value threshold to call a heterozygote (0.99) when running varscan somatic
    type: float
    default: 0.99
  - id: somatic_p_value
    doc: P-value threshold to call a somatic site (0.05)
    type: float
    default: 0.05
  - id: strand_filter
    doc: If set to 1, removes variants with >90% strand bias (0)
    type: ['null', int]
  - id: validation
    doc: If set to 1, outputs all compared positions even if non-variant
    type: ['null', int]
    default: 1
  - id: output_vcf
    doc: If set to 1, output VCF instead of VarScan native format
    type: ['null', int]
    default: 1
  - id: min_tumor_freq
    doc: Minimun variant allele frequency in tumor [0.10]
    type: float
    default: 0.10
  - id: max_normal_freq
    doc: Maximum variant allele frequency in normal [0.05]
    type: float
    default: 0.05
  - id: vps_p_value
    doc: P-value for high-confidence calling [0.07]
    type: float
    default: 0.07
  - id: ref_dict
    doc: reference sequence dictionary file
    type: File
outputs:
  - id: GERMLINE_ALL
    type:
      type: array
      items: File
    outputSource: varscan_process_somatic/GERMLINE_ALL
  - id: GERMLINE_HC
    type:
      type: array
      items: File
    outputSource: varscan_process_somatic/GERMLINE_HC
  - id: LOH_ALL
    type:
      type: array
      items: File
    outputSource: varscan_process_somatic/LOH_ALL
  - id: LOH_HC
    type:
      type: array
      items: File
    outputSource: varscan_process_somatic/LOH_HC
  - id: SOMATIC_ALL
    type:
      type: array
      items: File
    outputSource: varscan_process_somatic/SOMATIC_ALL
  - id: SOMATIC_HC
    type:
      type: array
      items: File
    outputSource: varscan_process_somatic/SOMATIC_HC
  - id: MAIN_OUTPUT
    type: File
    outputSource: mergevcf/output_vcf_file

steps:
  - id: samtools_workflow
    run: samtools_workflow.cwl
    in:
      - id: normal_input
        source: normal_input
      - id: tumor_input
        source: tumor_input
      - id: region
        source: region
      - id: reference
        source: reference
      - id: prefix
        source: prefix
    out:
      - id: chunk_mpileup

  - id: varscan_somatic
    run: ../tools/varscan_somatic.cwl
    in:
      - id: java_opts
        source: java_opts
      - id: tn_pair_pileup
        source: samtools_mpileup/output_file
      - id: output_basename
        source: prefix
      - id: output_snp
        source: prefix
        valueFrom: $(self + '_snp')
      - id: output_indel
        source: prefix
        valueFrom: $(self + '_indel')
      - id: min_coverage
        source: min_coverage
      - id: min_cov_normal
        source: min_cov_normal
      - id: min_cov_tumor
        source: min_cov_tumor
      - id: min_var_freq
        source: min_var_freq
      - id: min_freq_for_hom
        source: min_freq_for_hom
      - id: normal_purity
        source: normal_purity
      - id: tumor_purity
        source: tumor_purity
      - id: p_value
        source: vs_p_value
      - id: somatic_p_value
        source: somatic_p_value
      - id: strand_filter
        source: strand_filter
      - id: validation
        source: validation
      - id: output_vcf
        source: output_vcf
    out:
      - id: snp_output
      - id: indel_output

  - id: varscan_process_somatic
    run: varscan_process_somatic_workflow.cwl
    scatter: varscan_process_somatic/input_vcf
    in:
      - id: java_opts
        source: java_opts
      - id: input_vcf
        source: [varscan_somatic/snp_output, varscan_somatic/indel_output]
      - id: min_tumor_freq
        source: min_tumor_freq
      - id: max_normal_freq
        source: max_normal_freq
      - id: p_value
        source: vps_p_value
      - id: ref_dict
        source: ref_dict
    out:
      - id: GERMLINE_ALL
      - id: GERMLINE_HC
      - id: LOH_ALL
      - id: LOH_HC
      - id: SOMATIC_ALL
      - id: SOMATIC_HC

  - id: mergevcf
    run: ../tools/picard_mergevcf.cwl
    in:
      - id: java_opts
        source: java_opts
      - id: input_vcf
        source: varscan_process_somatic/SOMATIC_HC
      - id: output_filename
        source: prefix
        valueFrom: $(self + '_varscan2.snp.indel.somatic.hc.updated.merged.vcf')
      - id: ref_dict
        source: ref_dict
    out:
      - id: output_vcf_file
