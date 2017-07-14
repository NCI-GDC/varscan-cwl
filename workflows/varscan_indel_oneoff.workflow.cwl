#!/usr/bin/env cwlrunner

cwlVersion: v1.0

class: Workflow

requirements:
  - class: InlineJavascriptRequirement
  - class: StepInputExpressionRequirement
  - class: MultipleInputFeatureRequirement

inputs:
  hc_snp_vcf:
    type: File
    doc: VarScan high-confidence snp VCF (should be decompressed)
  raw_indel_vcf:
    type: File
    doc: VarScan raw indel VCF (should be decompressed)
  varscan_biasfiltered_vcf:
    type: File
    doc: The varscan annotated and biasfiltered SNP VCF
  tumor_bam:
    type: File
    doc: The tumor bam file
  tumor_index:
    type: File
    doc: The tumor bam index file
  raw_uuid:
    type: string
    doc: The UUID of the raw VCF output file
  annotated_uuid:
    type: string
    doc: The UUID of the annotated VCF output file
  full_sequence_dictionary:
    type: File
    doc: The sequence dictionary of the full GRCh38 reference
  full_reference_fasta:
    type: File
    doc: The GDC full fasta file
  main_reference_fai:
    type: File
    doc: The GDC main chromosomes only fai file
  main_sequence_dictionary:
    type: File
    doc: The sequence dictionary of the main GDC chromosomes only
  vep_fasta:
    type: File
    doc: The VEP top-level fasta file
  vep_forks:
    type: int
    doc: The number of VEP forks to use
  cache:
    type: Directory
    doc: The VEP cache directory
  gdc_entrez:
    type: File
    doc: GDC ENTREZ JSON file for VEP plugin
  gdc_evidence:
    type: File
    doc: GDC evidence vcf
  python:
    type: string
    doc: path to python executable for process_snp step
  script:
    type: string
    doc: path to python script for process_snp step

outputs:
  indel_germline_all:
    type: File
    outputSource: gzip_germline_all/output_file 
  indel_germline_hc:
    type: File
    outputSource: gzip_germline_hc/output_file 
  indel_loh_all:
    type: File
    outputSource: gzip_loh_all/output_file 
  indel_loh_hc:
    type: File
    outputSource: gzip_loh_hc/output_file 
  indel_somatic_all:
    type: File
    outputSource: gzip_somatic_all/output_file 
  indel_somatic_hc:
    type: File
    outputSource: gzip_somatic_hc/output_file 
  merged_vcf:
    type: File
    outputSource: merge_vcfs/output_vcf_file
  fpfilter_time_record:
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
    outputSource: fpfilter/time_record

  vep_stats_file:
    type: File
    outputSource: vep/stats_file

  vep_time_record:
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
    outputSource: vep/time_record

  final_annotated_vcf:
    type: File
    outputSource: final_format/output_file

steps:
  process_somatic:
    run: ../tools/ProcessSomatic.cwl
    in:
      - {id: input_vcf, source: raw_indel_vcf}
    out:
      - id: germline_all
      - id: germline_hc
      - id: loh_all
      - id: loh_hc
      - id: somatic_all
      - id: somatic_hc

  snp_update_dictionary:
    run: ../tools/UpdateSequenceDictionary.cwl
    in:
      - {id: input_vcf, source: hc_snp_vcf}
      - {id: sequence_dictionary, source: full_sequence_dictionary}
      - {id: output_filename, source: raw_uuid, valueFrom: "$(self + '.snp.Somatic.hc.update.vcf')"}
    out:
      - id: output_vcf_file

  indel_update_dictionary:
    run: ../tools/UpdateSequenceDictionary.cwl
    in:
      - {id: input_vcf, source: process_somatic/somatic_hc}
      - {id: sequence_dictionary, source: full_sequence_dictionary}
      - {id: output_filename, source: raw_uuid, valueFrom: "$(self + '.indel.Somatic.hc.update.vcf')"}
    out:
      - id: output_vcf_file

  merge_vcfs:
    run: ../tools/MergeVcfs.cwl
    in:
      - {id: input_vcf, source: [snp_update_dictionary/output_vcf_file, indel_update_dictionary/output_vcf_file]}
      - {id: sequence_dictionary, source: full_sequence_dictionary}
      - {id: output_filename, source: raw_uuid, valueFrom: "$(self + '.vcf.gz')"}
    out:
      - id: output_vcf_file 

  gzip_germline_all:
    run: ../tools/gzip.cwl
    in:
      - {id: input_file, source: process_somatic/germline_all}
      - {id: output_filename, source: raw_uuid, valueFrom: "$(self + '.indel.Germline.vcf.gz')"}
    out:
      - id: output_file

  gzip_germline_hc:
    run: ../tools/gzip.cwl
    in:
      - {id: input_file, source: process_somatic/germline_hc}
      - {id: output_filename, source: raw_uuid, valueFrom: "$(self + '.indel.Germline.hc.vcf.gz')"}
    out:
      - id: output_file

  gzip_loh_all:
    run: ../tools/gzip.cwl
    in:
      - {id: input_file, source: process_somatic/loh_all}
      - {id: output_filename, source: raw_uuid, valueFrom: "$(self + '.indel.LOH.vcf.gz')"}
    out:
      - id: output_file

  gzip_loh_hc:
    run: ../tools/gzip.cwl
    in:
      - {id: input_file, source: process_somatic/loh_hc}
      - {id: output_filename, source: raw_uuid, valueFrom: "$(self + '.indel.LOH.hc.vcf.gz')"}
    out:
      - id: output_file

  gzip_somatic_all:
    run: ../tools/gzip.cwl
    in:
      - {id: input_file, source: process_somatic/somatic_all}
      - {id: output_filename, source: raw_uuid, valueFrom: "$(self + '.indel.Somatic.vcf.gz')"}
    out:
      - id: output_file

  gzip_somatic_hc:
    run: ../tools/gzip.cwl
    in:
      - {id: input_file, source: process_somatic/somatic_hc}
      - {id: output_filename, source: raw_uuid, valueFrom: "$(self + '.indel.Somatic.hc.vcf.gz')"}
    out:
      - id: output_file

  split_vcfs:
    run: ../tools/SplitVcfs.cwl
    in:
      - {id: input_vcf, source: merge_vcfs/output_vcf_file}
      - {id: sequence_dictionary, source: full_sequence_dictionary}
      - {id: snv_filename, source: annotated_uuid, valueFrom: "$(self + '.snp.vcf')"}
      - {id: indel_filename, source: annotated_uuid, valueFrom: "$(self + '.indel.vcf')"}
    out:
      - id: output_snv_file
      - id: output_indel_file

  filter_chroms:
    run: ../tools/contigfilter.cwl
    in:
      - {id: input_vcf, source: split_vcfs/output_indel_file}
      - {id: fai, source: main_reference_fai}
      - {id: output_vcf, source: annotated_uuid, valueFrom: "$(self + '.contig_filtered.vcf')"}
    out:
      - id: vcf_out

  fpfilter:
    run: ../tools/fpfilter.cwl
    in:
      - {id: input_vcf, source: filter_chroms/vcf_out}
      - {id: bam_file, source: tumor_bam}
      - {id: bam_index, source: tumor_index}
      - {id: sample, default: "TUMOR"}
      - {id: reference, source: full_reference_fasta}
      - {id: output_filename, source: annotated_uuid, valueFrom: "$(self + '.fpfilter.vcf')"}
    out:
      - id: vcf_out
      - id: time_record

  process_snp:
    run: ../tools/ProcessSnpVcf.cwl
    in:
      - {id: python, source: python}
      - {id: script, source: script}
      - {id: input_snp_vcf, source: varscan_biasfiltered_vcf}
      - {id: output_filename, source: annotated_uuid, valueFrom: "$(self + '.biasfiltered.snp.vcf')"}
    out:
      - id: output_vcf_file

  merge_fpfilter_vcfs:
    run: ../tools/MergeVcfs.cwl
    in:
      - {id: input_vcf, source: [process_snp/output_vcf_file, fpfilter/vcf_out]}
      - {id: sequence_dictionary, source: main_sequence_dictionary}
      - {id: output_filename, source: annotated_uuid, valueFrom: "$(self + '.merged.vcf.gz')"}
    out:
      - id: output_vcf_file

  reheader_vcf:
    run: ../tools/ReheaderVcf.cwl
    in:
      - {id: input_snp_vcf, source: process_snp/output_vcf_file}
      - {id: input_merged_vcf, source: merge_fpfilter_vcfs/output_vcf_file}
      - {id: output_filename, source: annotated_uuid, valueFrom: "$(self + '.merged.reheader.vcf')"}
    out:
      - id: output_vcf_file

  vep:
    run: ../tools/vep.cwl
    in:
      - {id: input_file, source: reheader_vcf/output_vcf_file}
      - {id: fasta, source: vep_fasta}
      - {id: dir_cache, source: cache}
      - {id: output_file, source: annotated_uuid, valueFrom: "$(self + '.vep.raw.vcf')"}
      - {id: vcf, default: true}
      - {id: stats_filename, source: annotated_uuid, valueFrom: "$(self + '.vep.stats.txt')"}
      - {id: stats_text, default: true}
      - {id: fork, source: vep_forks}
      - {id: everything, default: true}
      - {id: xref_refseq, default: true}
      - {id: total_length, default: true}
      - {id: allele_number, default: true}
      - {id: check_alleles, default: true}
      - {id: assembly, default: "GRCh38"}
      - {id: gdc_entrez, source: gdc_entrez}
      - {id: gdc_evidence, source: gdc_evidence}
    out:
      - id: vep_out
      - id: stats_file
      - id: warning_file
      - id: time_record

  final_format:
    run: ../tools/VcfFormatConverter.cwl
    in:
      - {id: input_vcf, source: vep/vep_out}
      - {id: output_filename, source: annotated_uuid, valueFrom: "$(self + '.vep.vcf.gz')"}
    out:
      - id: output_file
