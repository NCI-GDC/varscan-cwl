#!/usr/bin/env cwl-runner

cwlVersion: v1.0

doc: |
    Run fpfilter 

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/variant-filtration-tool:0.1 

class: CommandLineTool

inputs:
  input_vcf:
    type: File
    doc: The VCF file to process 
    inputBinding:
      prefix: --vcf-file 

  bam_file:
    type: File
    doc: The BAM file to process
    inputBinding:
      prefix: --bam-file

  bam_index:
    type: File
    doc: The BAM index file 
    inputBinding:
      prefix: --bam-index

  sample:
    type: string
    doc: The sample name of the sample you want to filter on in the VCF
    inputBinding:
      prefix: --sample

  reference:
    type: File
    doc: reference fasta file
    inputBinding:
      prefix: --reference
    secondaryFiles:
      - ".fai"

  output_filename:
    type: string
    doc: "the filename of the output VCF file"
    inputBinding:
        prefix: --output

  min_read_pos:
    type: float?
    doc: "minimum average relative distance from start/end of read [0.10]"
    inputBinding:
        prefix: --min-read-pos

  min_var_freq:
    type: float?
    doc: "minimum variant allele frequency [0.05]"
    inputBinding:
        prefix: --min-var-freq

  min_var_count:
    type: int?
    doc: "minimum number of variant-supporting reads [4]"
    inputBinding:
        prefix: --min-var-count

  min_strandedness:
    type: float?
    doc: "minimum representation of variant allele on each strand [0.01]"
    inputBinding:
        prefix: --min-strandedness

  max_mm_qualsum_diff:
    type: int?
    doc: "maximum difference of mismatch quality sum between variant and reference reads (paralog filter) [50]"
    inputBinding:
        prefix: --max-mm-qualsum-diff

  max_var_mm_qualsum:
    type: int?
    label: "Max var qualsum"
    doc: "maximum mismatch quality sum of reference-supporting reads [100]"
    inputBinding:
        prefix: --max_var_mm_qualsum

  max_mapqual_diff:
    type: int?
    label: "Max mapqual diff"
    doc: "maximum difference of mapping quality between variant and reference reads [30]"
    inputBinding:
        prefix: --max-mapqual-diff

  max_readlen_diff:
    type: int?
    doc: "maximum difference of average supporting read length between variant and reference reads (paralog filter) [25]"
    inputBinding:
        prefix: --max-readlen-diff

  min_var_dist_3:
    type: float?
    doc: "minimum average distance to effective 3prime end of read (real end or Q2) for variant-supporting reads [0.20]"
    inputBinding:
        prefix: --min-var-dist-3


outputs:
  vcf_out:
    type: File
    doc: Filtered VCF file
    outputBinding:
      glob: $(inputs.output_filename)

  time_record:
    type:
      type: record
      name: time_record
      label: Time output
      fields:
        real_time:
          type: string
        user_time:
          type: float
        system_time:
          type: float
        wall_clock:
          type: float
        maximum_resident_set_size:
          type: int
        percent_of_cpu:
          type: string
    outputBinding:
      loadContents: true
      glob: $(inputs.output_filename.substr(0, inputs.output_filename.lastIndexOf('.')) + '.time.json')
      outputEval: |
        ${
           var data = JSON.parse(self[0].contents);
           return data;
         }

baseCommand: [/usr/bin/time]

arguments:
  - valueFrom: "{\"real_time\": \"%E\", \"user_time\": %U, \"system_time\": %S, \"wall_clock\": %e, \"maximum_resident_set_size\": %M, \"percent_of_cpu\": \"%P\"}"
    position: -10
    prefix: -f

  - valueFrom: $(inputs.output_filename.substr(0, inputs.output_filename.lastIndexOf('.')) + '.time.json')
    position: -9
    prefix: -o

  - valueFrom: /usr/bin/perl 
    position: -8

  - valueFrom: /home/ubuntu/tools/fpfilter-tool/fpfilter.pl 
    position: -7
