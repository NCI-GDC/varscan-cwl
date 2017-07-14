#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.0
doc: |
    Gzips a file 

requirements:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/gdc-biasfilter-tool:0.3
  - class: InlineJavascriptRequirement

inputs:
  input_file:
    type: File
    doc: file to compress 
    inputBinding:
      position: 0 

  output_filename:
    type: string
    doc: output basename of file 

outputs:
  output_file:
    type: File
    doc: gzip compressed file 
    streamable: true
    outputBinding:
      glob: $(inputs.output_filename)

stdout: $(inputs.output_filename)

baseCommand: [/bin/gzip, -c]
