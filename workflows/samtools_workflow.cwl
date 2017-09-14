#!/usr/bin/env cwl-runner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement
  - class: SubworkflowFeatureRequirement

inputs:
  - id: normal_input
    type: File
  - id: tumor_input
    type: File
  - id: min_MQ
    type: int
  - id: region
    type: string
  - id: reference
    type: File
  - id: prefix
    type: string

outputs:
  - id: chunk_mpileup
    type: File
    outputSource: mpileup_pair/output_file

steps:
  - id: split
    run: samtools_split_workflow.cwl
    in:
      - id: normal_input
        source: normal_input
      - id: tumor_input
        source: tumor_input
      - id: region
        source: region
      - id: prefix
        source: prefix
    out:
      - id: normal_chunk
      - id: tumor_chunk

  - id: mpileup_pair
    run: ../tools/samtools_mpileup.cwl
    in:
      - id: ref
        source: reference
      - id: region
        source: region
      - id: min_MQ
        source: min_MQ
      - id: normal_bam
        source: split/normal_chunk
      - id: tumor_bam
        source: split/tumor_chunk
      - id: output
        source: prefix
        valueFrom: $(self + '.mpileup')
    out:
      - id: output_file
