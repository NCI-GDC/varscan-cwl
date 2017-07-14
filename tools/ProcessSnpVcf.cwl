#!/usr/bin/env cwl-runner

class: CommandLineTool

cwlVersion: v1.0
doc: |
    A tool for removing the VEP annotations from the INFO column and header 

requirements:
  - class: InlineJavascriptRequirement

inputs:
  python:
    type: string
    doc: path to the python executable
    inputBinding:
      position: 0

  script:
    type: string
    doc: path to the script
    inputBinding:
      position: 1

  input_snp_vcf:
    type: File
    doc: Absolute filename of formatted SNV VCF from biasfilter pipeline 
    inputBinding:
      position: 2 

  output_filename:
    type: string
    doc: filename of output VCF file 
    inputBinding:
      position: 3 

outputs:
  output_vcf_file:
    type: File
    outputBinding:
      glob: $(inputs.output_filename) 
    doc: The output VCF file 

baseCommand: []
