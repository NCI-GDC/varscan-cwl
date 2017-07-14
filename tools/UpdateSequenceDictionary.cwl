#!/usr/bin/env cwl-runner

class: CommandLineTool
label: "Picard UpdateVcfSequenceDictionary"
cwlVersion: v1.0
doc: |
    Updates sequence dictionary with picard 

requirements:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/gdc-biasfilter-tool:0.3
  - class: InlineJavascriptRequirement

inputs:
  input_vcf:
    type: File
    doc: input VCF file
    inputBinding:
      prefix: INPUT=
      separate: false 

  sequence_dictionary:
    type: File
    doc: reference sequence dictionary file
    inputBinding:
      prefix: SEQUENCE_DICTIONARY=
      separate: false

  output_filename:
    type: string
    doc: output basename of file 
    inputBinding:
      prefix: OUTPUT=
      separate: false

outputs:
  output_vcf_file:
    type: File
    doc: Updated sequence dictionary vcf 
    outputBinding:
      glob: $(inputs.output_filename)


baseCommand: [java, -Xmx4G, -jar, /home/ubuntu/tools/picard-2.9.0/picard.jar, UpdateVcfSequenceDictionary]
