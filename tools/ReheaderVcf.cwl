#!/usr/bin/env cwl-runner

class: CommandLineTool

cwlVersion: v1.0
doc: |
    A Docker container for reheadering the VCF file from biasfilter workflow 

requirements:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/gdc-biasfilter-tool:0.3
  - class: InlineJavascriptRequirement

inputs:
  input_snp_vcf:
    type: File
    doc: Absolute filename of formatted SNV VCF from biasfilter pipeline 
    inputBinding:
      position: 0 

  input_merged_vcf:
    type: File
    doc: Absolute filename of merged VCF file 
    inputBinding:
      position: 1 

  output_filename:
    type: string
    doc: filename of output VCF file 
    inputBinding:
      position: 2 

outputs:
  output_vcf_file:
    type: File
    outputBinding:
      glob: $(inputs.output_filename) 
    doc: The output VCF file 

baseCommand: [/home/ubuntu/.virtualenvs/p2/bin/python, /home/ubuntu/tools/gdc-biasfilter-tool/ReheaderVcf.py]
