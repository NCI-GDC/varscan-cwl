#!/usr/bin/env cwl-runner

cwlVersion: v1.0

doc: |
    Run SAMtools mpileup

requirements:
  - class: InlineJavascriptRequirement
  - class: ShellCommandRequirement
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/samtools:1.1

class: CommandLineTool

inputs:
  - id: ref
    type: File
    inputBinding:
      position: 1
      prefix: -f
    secondaryFiles:
      - '.fai'

  - id: min_MQ
    type: int
    doc: skip alignments with mapQ smaller than INT [0]
    default: 1
    inputBinding:
      position: 2
      prefix: -q

  - id: region
    type: string
    inputBinding:
      position: 4
      prefix: -r

  - id: normal_bam
    type: File
    inputBinding:
      position: 5
    secondaryFiles:
      - '^.bai'

  - id: tumor_bam
    type: File
    inputBinding:
      position: 6
    secondaryFiles:
      - '^.bai'

  - id: output
    type: string
    inputBinding:
      position: 7
      prefix: ">"

outputs:
  - id: output_file
    type: File
    outputBinding:
      glob: $(inputs.output)

baseCommand: ['samtools', 'mpileup']
arguments:
  - valueFrom: '-B'
    position: 3
