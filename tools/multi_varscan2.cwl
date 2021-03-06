class: CommandLineTool
cwlVersion: v1.0
id: multi_varscan2
requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/varscan-tool:1.0.0-27.54c3e1f
doc: |
    Multithreading on VarScan.v2.3.9.

inputs:
  thread_count:
    type: int
    inputBinding:
      prefix: '--thread-count'

  java_opts:
    type: string
    default: '3G'
    doc: |
      "JVM arguments should be a quoted, space separated list (e.g. -Xmx8g -Xmx16g -Xms128m -Xmx512m)"
    inputBinding:
      prefix: --java-opts

  tn_pair_pileup:
    doc: The SAMtools pileup file for tumor/normal pair
    type:
      type: array
      items: File
      inputBinding:
        prefix: --mpileup

  ref_dict:
    type: File
    doc: reference sequence dictionary file
    inputBinding:
      prefix: --ref-dict

  min_coverage:
    doc: Minimum coverage in normal and tumor to call variant (8)
    type: int
    default: 8
    inputBinding:
      prefix: --min-coverage

  min_cov_normal:
    doc: Minimum coverage in normal to call somatic (8)
    type: int
    default: 8
    inputBinding:
      prefix: --min-cov-normal

  min_cov_tumor:
    doc: Minimum coverage in tumor to call somatic (6)
    type: int
    default: 6
    inputBinding:
      prefix: --min-cov-tumor

  min_var_freq:
    doc: Minimum variant frequency to call a heterozygote (0.10)
    type: float
    default: 0.10
    inputBinding:
      prefix: --min-var-freq

  min_freq_for_hom:
    doc: Minimum frequency to call homozygote (0.75)
    type: float
    default: 0.75
    inputBinding:
      prefix: --min-freq-for-hom

  normal_purity:
    doc: Estimated purity (non-tumor content) of normal sample (1.00)
    type: float
    default: 1.00
    inputBinding:
      prefix: --normal-purity

  tumor_purity:
    doc: Estimated purity (tumor content) of tumor sample (1.00)
    type: float
    default: 1.00
    inputBinding:
      prefix: --tumor-purity

  vs_p_value:
    doc: P-value threshold to call a heterozygote (0.99)
    type: float
    default: 0.99
    inputBinding:
      prefix: --vs-p-value

  somatic_p_value:
    doc: P-value threshold to call a somatic site (0.05)
    type: float
    default: 0.05
    inputBinding:
      prefix: --somatic-p-value

  strand_filter:
    doc: If set to 1, removes variants with >90% strand bias (0)
    type: int
    inputBinding:
      prefix: --strand-filter

  validation:
    doc: If set, outputs all compared positions even if non-variant
    type: boolean
    inputBinding:
      prefix: --validation

  output_vcf:
    doc: If set to 1, output VCF instead of VarScan native format
    type: int
    inputBinding:
      prefix: --output-vcf

  min_tumor_freq:
    type: float
    doc: Minimun variant allele frequency in tumor [0.10]
    default: 0.10
    inputBinding:
      prefix: --min-tumor-freq

  max_normal_freq:
    type: float
    doc: Maximum variant allele frequency in normal [0.05]
    default: 0.05
    inputBinding:
      prefix: --max-normal-freq

  vps_p_value:
    type: float
    doc: P-value for high-confidence calling [0.07]
    default: 0.07
    inputBinding:
      prefix: --vps-p-value

  timeout:
    type: int?
    inputBinding:
      position: 99
      prefix: --timeout
outputs:
  SNP_SOMATIC_HC:
    type: File
    outputBinding:
      glob: 'multi_varscan2_snp_merged.vcf'
  INDEL_SOMATIC_HC:
    type: File
    outputBinding:
      glob: 'multi_varscan2_indel_merged.vcf'

baseCommand: ''
