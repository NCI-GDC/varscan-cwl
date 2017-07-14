#!/usr/bin/env cwl-runner

cwlVersion: v1.0

doc: |
    Run Varscan processSomatic

requirements:
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
      - $(inputs.input_vcf)

hints:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/varscan-tool:mpileup

class: CommandLineTool

inputs:
  input_vcf:
    type: File
    doc: The VarScan output file for SNPs or InDels
    inputBinding:
      position: 0
      valueFrom: $(self.basename)

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
      prefix: --maf-normal-freq

  p_value:
    type: float
    doc: P-value for high-confidence calling [0.07]
    default: 0.07
    inputBinding:
      prefix: --p-value

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

baseCommand: [java, -Xmx2G, -jar, /home/ubuntu/bin/VarScan.jar, processSomatic]
