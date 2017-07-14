#!/usr/bin/env cwl-runner

class: CommandLineTool
label: "Picard MergeVcfs"
cwlVersion: v1.0
doc: |
    Merge VCFs together.

requirements:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/gdc-biasfilter-tool:0.3
  - class: InlineJavascriptRequirement

inputs:
  input_vcf:
    type:
      type: array
      items: File
      inputBinding:
        prefix: I=
        separate: false
    doc: "input vcf files"

  sequence_dictionary:
    type: File
    doc: reference sequence dictionary file
    inputBinding:
      prefix: SEQUENCE_DICTIONARY=
      separate: false

  output_filename:
    type: string
    doc: output basename of merged
    inputBinding:
      prefix: OUTPUT=
      separate: false

outputs:
  output_vcf_file:
    type: File
    outputBinding:
      glob: $(inputs.output_filename)
    doc: Merged VCF file
    secondaryFiles:
      - ".tbi"

baseCommand: [java, -Xmx4G, -jar, /home/ubuntu/tools/picard-2.9.0/picard.jar, MergeVcfs]
