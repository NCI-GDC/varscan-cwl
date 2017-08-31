#!/usr/bin/env cwl-runner

cwlVersion: v1.0

doc: |
    Run VarScan.v2.3.9 somatic

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/varscan-tool:2.3.9

class: CommandLineTool

inputs:
  - id: java_opts
    type: string
    default: '3G'
    doc: |
      "JVM arguments should be a quoted, space separated list (e.g. -Xmx8g -Xmx16g -Xms128m -Xmx512m)"
    inputBinding:
      position: 3
      prefix: '-Xmx'
      separate: false

  - id: tn_pair_pileup
    doc: The SAMtools pileup file for tumor/normal pair
    type: File
    inputBinding:
      position: 6

  - id: output_basename
    doc: Output base name for SNP and indel output
    type: string
    inputBinding:
      position: 7

  - id: output_snp
    doc: Output file for SNP calls (output.snp)
    type: string
    inputBinding:
      position: 9
      prefix: '--output-snp'

  - id: output_indel
    doc: Output file for indel calls (output.indel)
    type: string
    inputBinding:
      position: 10
      prefix: '--output-indel'

  - id: min_coverage
    doc: Minimum coverage in normal and tumor to call variant (8)
    type: int
    default: 8
    inputBinding:
      position: 11
      prefix: '--min-coverage'

  - id: min_cov_normal
    doc: Minimum coverage in normal to call somatic (8)
    type: int
    default: 8
    inputBinding:
      position: 12
      prefix: '--min-coverage-normal'

  - id: min_cov_tumor
    doc: Minimum coverage in tumor to call somatic (6)
    type: int
    default: 6
    inputBinding:
      position: 13
      prefix: '--min-coverage-tumor'

  - id: min_var_freq
    doc: Minimum variant frequency to call a heterozygote (0.10)
    type: float
    default: 0.10
    inputBinding:
      position: 14
      prefix: '--min-var-freq'

  - id: min_freq_for_hom
    doc: Minimum frequency to call homozygote (0.75)
    type: float
    default: 0.75
    inputBinding:
      position: 15
      prefix: '--min-freq-for-hom'

  - id: normal_purity
    doc: Estimated purity (non-tumor content) of normal sample (1.00)
    type: float
    default: 1.00
    inputBinding:
      position: 16
      prefix: '--normal-purity'

  - id: tumor_purity
    doc: Estimated purity (tumor content) of tumor sample (1.00)
    type: float
    default: 1.00
    inputBinding:
      position: 17
      prefix: '--tumor-purity'

  - id: p_value
    doc: P-value threshold to call a heterozygote (0.99)
    type: float
    default: 0.99
    inputBinding:
      position: 18
      prefix: '--p-value'

  - id: somatic_p_value
    doc: P-value threshold to call a somatic site (0.05)
    type: float
    default: 0.05
    inputBinding:
      position: 19
      prefix: '--somatic-p-value'

  - id: strand_filter
    doc: If set to 1, removes variants with >90% strand bias (0)
    type: ['null', int]
    inputBinding:
      position: 20
      prefix: '--strand-filter'

  - id: validation
    doc: If set to 1, outputs all compared positions even if non-variant
    type: ['null', int]
    inputBinding:
      position: 21
      prefix: '--validation'

  - id: output_vcf
    doc: If set to 1, output VCF instead of VarScan native format
    type: ['null', int]
    inputBinding:
      position: 22
      prefix: '--output-vcf'

outputs:
  - id: validation_output
    type: File
    outputBinding:
      glob: $(inputs.output_basename + '.validation')

  - id: snp_output
    type: File
    outputBinding:
      glob: $(inputs.output_snp + '.vcf')

  - id: indel_output
    type: File
    outputBinding:
      glob: $(inputs.output_indel + '.vcf')

baseCommand: ['java', '-d64', '-XX:+UseSerialGC']
arguments:
  - valueFrom: '/home/ubuntu/VarScan.v2.3.9.jar'
    prefix: "-jar"
    position: 4
  - valueFrom: 'somatic'
    position: 5
  - valueFrom: '1'
    position: 8
    prefix: '--mpileup'
