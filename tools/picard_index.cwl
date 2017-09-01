#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: CommandLineTool

requirements:
  - class: InlineJavascriptRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/picard
  - class: InitialWorkDirRequirement
    listing:
      - entry: $(inputs.input_bam)
        entryname: $(inputs.input_bam.basename)
        writable: True

inputs:
  - id: java_opts
    type: string
    default: '16G'
    doc: |
      'JVM arguments should be a quoted, space separated list (e.g. -Xmx8g -Xmx16g -Xms128m -Xmx512m)'
    inputBinding:
      position: 3
      prefix: '-Xmx'
      separate: false

  - id: input_bam
    type: File
    inputBinding:
      prefix: 'I='
      separate: false
      position: 7
      valueFrom: $(self.basename)

outputs:
  - id: bam_with_index
    type: File
    outputBinding:
      glob: $(inputs.input_bam.basename)
    secondaryFiles:
      - '^.bai'

baseCommand: ['java', '-d64', '-XX:+UseSerialGC']
arguments:
  - valueFrom: '/usr/local/bin/picard.jar'
    prefix: '-jar'
    position: 5
  - valueFrom: 'BuildBamIndex'
    position: 6
