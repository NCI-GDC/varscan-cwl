#!/usr/bin/env cwl-runner

class: CommandLineTool
label: "Picard SplitVcfs" 
cwlVersion: v1.0
doc: |
    Split a VCF file into InDels and SNVs 

requirements:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/gdc-biasfilter-tool:0.3
  - class: InlineJavascriptRequirement

inputs:
  input_vcf:
    type: File
    doc: "input vcf file"
    inputBinding:
      prefix: "INPUT="
      separate: false 
    secondaryFiles:
      - ".tbi"

  sequence_dictionary: 
    type: File
    doc: reference sequence dictionary file 
    inputBinding:
      prefix: "SEQUENCE_DICTIONARY="
      separate: false 

  snv_filename: 
    type: string 
    default: snv.vcf
    doc: output basename of SNV file 
    inputBinding:
      prefix: "SNP_OUTPUT="
      separate: false 

  indel_filename: 
    type: string 
    default: indel.vcf
    doc: output basename of INDEL file 
    inputBinding:
      prefix: "INDEL_OUTPUT="
      separate: false 

outputs:
  output_snv_file:
    type: File
    outputBinding:
      glob: $(inputs.snv_filename) 
    doc: SNV VCF File 
    secondaryFiles:
      - ".idx"

  output_indel_file:
    type: File
    outputBinding:
      glob: $(inputs.indel_filename) 
    doc: INDEL VCF File 
    secondaryFiles:
      - ".idx"

baseCommand: [java, -Xmx4G, -jar, /home/ubuntu/tools/picard-2.9.0/picard.jar, SplitVcfs]
