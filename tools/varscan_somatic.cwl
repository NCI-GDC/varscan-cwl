class: CommandLineTool
cwlVersion: v1.0
id: varscan_somatic
requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/varscan-tool:2.3.9
  - class: ResourceRequirement
    coresMax: 1
doc: |
    VarScan2 somatic calling.

inputs:
  java_opts:
    type: string
    default: '3G'
    doc: |
      "JVM arguments should be a quoted, space separated list (e.g. -Xmx8g -Xmx16g -Xms128m -Xmx512m)"
    inputBinding:
      position: 0
      prefix: '-Xmx'
      separate: false

  tn_pair_pileup:
    doc: The SAMtools pileup file for tumor/normal pair
    type: File
    inputBinding:
      position: 3

  min_coverage:
    doc: Minimum coverage in normal and tumor to call variant (8)
    type: int
    default: 8
    inputBinding:
      position: 11
      prefix: '--min-coverage'

  min_cov_normal:
    doc: Minimum coverage in normal to call somatic (8)
    type: int
    default: 8
    inputBinding:
      position: 12
      prefix: '--min-coverage-normal'

  min_cov_tumor:
    doc: Minimum coverage in tumor to call somatic (6)
    type: int
    default: 6
    inputBinding:
      position: 13
      prefix: '--min-coverage-tumor'

  min_var_freq:
    doc: Minimum variant frequency to call a heterozygote (0.10)
    type: float
    default: 0.10
    inputBinding:
      position: 14
      prefix: '--min-var-freq'

  min_freq_for_hom:
    doc: Minimum frequency to call homozygote (0.75)
    type: float
    default: 0.75
    inputBinding:
      position: 15
      prefix: '--min-freq-for-hom'

  normal_purity:
    doc: Estimated purity (non-tumor content) of normal sample (1.00)
    type: float
    default: 1.00
    inputBinding:
      position: 16
      prefix: '--normal-purity'

  tumor_purity:
    doc: Estimated purity (tumor content) of tumor sample (1.00)
    type: float
    default: 1.00
    inputBinding:
      position: 17
      prefix: '--tumor-purity'

  p_value:
    doc: P-value threshold to call a heterozygote (0.99)
    type: float
    default: 0.99
    inputBinding:
      position: 18
      prefix: '--p-value'

  somatic_p_value:
    doc: P-value threshold to call a somatic site (0.05)
    type: float
    default: 0.05
    inputBinding:
      position: 19
      prefix: '--somatic-p-value'

  strand_filter:
    doc: If set to 1, removes variants with >90% strand bias (0)
    type: int
    inputBinding:
      position: 20
      prefix: '--strand-filter'

  validation:
    doc: If set, outputs all compared positions even if non-variant
    type: boolean
    inputBinding:
      position: 21
      prefix: '--validation'

  output_vcf:
    doc: If set to 1, output VCF instead of VarScan native format
    type: int
    inputBinding:
      position: 22
      prefix: '--output-vcf'

outputs:
  snp_output:
    type: File
    outputBinding:
      glob: $(inputs.tn_pair_pileup.nameroot + '.snp.vcf')

  indel_output:
    type: File
    outputBinding:
      glob: $(inputs.tn_pair_pileup.nameroot + '.indel.vcf')

baseCommand: ['java', '-d64', '-XX:+UseSerialGC']
arguments:
  - valueFrom: '/opt/VarScan.v2.3.9.jar'
    prefix: "-jar"
    position: 1
  - valueFrom: 'somatic'
    position: 2
  - valueFrom: $(inputs.tn_pair_pileup.nameroot)
    position: 4
  - valueFrom: '1'
    position: 5
    prefix: '--mpileup'
