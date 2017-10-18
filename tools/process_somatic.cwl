#!/usr/bin/env cwl-runner

cwlVersion: v1.0

doc: |
    Run Varscan processSomatic

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/varscan-tool:2.3.9
  - class: InitialWorkDirRequirement
    listing:
      - entry: $(inputs.input_vcf)
        entryname: $(inputs.input_vcf.basename)
        writable: True
  - class: ResourceRequirement
  
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

  - id: input_vcf
    type: File
    doc: The VarScan output file for SNPs or InDels
    inputBinding:
      position: 6
      valueFrom: $(self.basename)

  - id: min_tumor_freq
    type: float
    doc: Minimun variant allele frequency in tumor [0.10]
    default: 0.10
    inputBinding:
      position: 7
      prefix: '--min-tumor-freq'

  - id: max_normal_freq
    type: float
    doc: Maximum variant allele frequency in normal [0.05]
    default: 0.05
    inputBinding:
      position: 8
      prefix: '--maf-normal-freq'

  - id: p_value
    type: float
    doc: P-value for high-confidence calling [0.07]
    default: 0.07
    inputBinding:
      position: 9
      prefix: '--p-value'

outputs:
  germline_all:
    type: File
    doc: All germline VCF
    outputBinding:
      glob: $(inputs.input_vcf.nameroot + '.Germline.vcf')

  germline_hc:
    type: File
    doc: HC germline VCF
    outputBinding:
      glob: $(inputs.input_vcf.nameroot + '.Germline.hc.vcf')

  loh_all:
    type: File
    doc: All loh VCF
    outputBinding:
      glob: $(inputs.input_vcf.nameroot + '.LOH.vcf')

  loh_hc:
    type: File
    doc: HC loh VCF
    outputBinding:
      glob: $(inputs.input_vcf.nameroot + '.LOH.hc.vcf')

  somatic_all:
    type: File
    doc: All somatic VCF
    outputBinding:
      glob: $(inputs.input_vcf.nameroot + '.Somatic.vcf')

  somatic_hc:
    type: File
    doc: HC somatic VCF
    outputBinding:
      glob: $(inputs.input_vcf.nameroot + '.Somatic.hc.vcf')

baseCommand: ['java', '-d64', '-XX:+UseSerialGC']
arguments:
  - valueFrom: '/home/ubuntu/VarScan.v2.3.9.jar'
    prefix: "-jar"
    position: 4
  - valueFrom: 'processSomatic'
    position: 5
