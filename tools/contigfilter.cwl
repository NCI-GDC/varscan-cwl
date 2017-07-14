#!/usr/bin/env cwl-runner

cwlVersion: v1.0

doc: |
    description: "Filtering contigs from VCF"
    Usage:  cwl-runner <this-file-path> options

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/vep-tool:0.2

class: CommandLineTool

inputs:
  input_vcf:
    type: File
    label: "Input VCF"
    doc: "Input VCF File"
    inputBinding:
        prefix: --input_vcf

  output_vcf:
    type: string
    label: "Output VCF"
    doc: "Path to output filtered/formatted VCF file"
    inputBinding:
        prefix: --output_vcf

  fai:
    type: File?
    label: "Fai"
    doc: "The FAI file containing the contigs you want to keep. Default is already in docker"
    inputBinding:
        prefix: --fai

  assembly:
    type: string
    default: "GRCh38.d1.vd1"
    label: "Assembly"
    doc: "The assembly name to use in VCF header"
    inputBinding:
        prefix: --assembly

  reference:
    type: string
    default: "GRCh38.d1.vd1.fa"
    label: "Reference Name"
    doc: "The reference fasta name to use in VCF header"
    inputBinding:
        prefix: --reference

outputs:
  vcf_out:
    type: File
    doc: Contig filtered VCF file
    outputBinding:
      glob: $(inputs.output_vcf)

baseCommand: [/home/ubuntu/.virtualenvs/p3/bin/python, /home/ubuntu/tools/vep-tool/main.py, contigfilter]
