#!/usr/bin/env cwl-runner

cwlVersion: v1.0

doc: |
    doc: "Running Variant Effect Predictor v84"
    Usage:  cwl-runner <this-file-path> options

requirements:
  - class: InlineJavascriptRequirement

hints:
  - class: DockerRequirement
    dockerPull: quay.io/ncigdc/vep-tool:0.2

class: CommandLineTool

inputs:
  input_file:
    type: File
    label: "Input File"
    doc: "path to file you wish to annotate"
    inputBinding:
        prefix: --input_file

  fasta:
    type: File
    label: "Reference fasta"
    doc: "path to reference file"
    inputBinding:
        prefix: --fasta
    secondaryFiles:
        - ".fai"
        - ".gzi"

  dir_cache:
    type: Directory 
    label: "Cache directory" 
    doc: "specific directory for cache" 
    inputBinding:
        prefix: --dir_cache

  dir_plugins:
    type: string 
    default: "/home/ubuntu/tools/vep-plugins" 
    label: "specific directory for plugins" 
    doc: "path to reference file"
    inputBinding:
        prefix: --dir_plugins

  output_file:
    type: string 
    label: "Output file" 
    doc: "output file name" 
    inputBinding:
        prefix: --output_file

  stats_filename:
    type: string? 
    label: "Statistics file" 
    doc: "the path to the output stats file (HTML is default type)" 
    inputBinding:
        prefix: --stats_file

  no_stats:
    type: boolean? 
    label: "No Stats" 
    doc: "if you don't want stats to be output" 
    inputBinding:
        prefix: --no_stats

  warning_filename:
    type: string?
    label: "Plugin directory" 
    doc: "file to write warnings to" 
    inputBinding:
        prefix: --warning_file

  stats_text:
    type: boolean?
    label: "Stats text" 
    doc: "output stats file as text instead of HTML" 
    inputBinding:
        prefix: --stats_text

  format:
    type: string
    default: "vcf"
    label: "Input file format" 
    doc: "input file format" 
    inputBinding:
        prefix: --format
        
  individual:
    type: string?
    label: "Individual" 
    doc: "only output variants from this individual in the vcf file" 
    inputBinding:
        prefix: --individual

  tabix:
    type: boolean?
    label: "Tabix flag" 
    doc: "bgzip and tabix-index output" 
    inputBinding:
        prefix: --tabix

  gvf:
    type: boolean?
    label: "Output gvf" 
    doc: "produce gvf output" 
    inputBinding:
        prefix: --gvf

  vcf:
    type: boolean?
    label: "Output vcf" 
    doc: "produce VCF output" 
    inputBinding:
        prefix: --vcf

  solr:
    type: boolean?
    label: "Output solr" 
    doc: "produce XML output for Solr" 
    inputBinding:
        prefix: --solr

  json:
    type: boolean?
    label: "Output JSON" 
    doc: "produce JSON document output" 
    inputBinding:
        prefix: --json

  tab:
    type: boolean?
    label: "Output tab-delimited" 
    doc: "produce tabulated output" 
    inputBinding:
        prefix: --tab

  vcf_info_field:
    type: string?
    label: "VCF info field" 
    doc: "allow user to change VCF info field name" 
    inputBinding:
        prefix: --vcf_info_field

  keep_csq:
    type: boolean?
    label: "Keep CSQ" 
    doc: "don't nuke existing CSQ fields in VCF" 
    inputBinding:
        prefix: --keep_csq

  keep_ann:
    type: boolean?
    label: "Keep ann" 
    doc: "synonym for keep_seq" 
    inputBinding:
        prefix: --keep_ann

  assembly:
    type: string
    default: "GRCh38"
    label: "Assembly" 
    doc: "assembly version to use" 
    inputBinding:
        prefix: --assembly

  chr:
    type: string?
    label: "Chromosomes" 
    doc: "analyze only these chromosomes, e.g., 1-5,10,MT" 
    inputBinding:
        prefix: --chr

  check_ref:
    type: boolean?
    label: "Check reference" 
    doc: "check supplied reference allele against DB" 
    inputBinding:
        prefix: --check_ref

  check_existing:
    type: boolean?
    label: "Check exisiting" 
    doc: "find existing co-located variations" 
    inputBinding:
        prefix: --check_existing

  check_svs:
    type: boolean?
    label: "Check SVS" 
    doc: "find overlapping structural variations" 
    inputBinding:
        prefix: --check_svs

  check_alleles:
    type: boolean?
    label: "Check alleles" 
    doc: "only attribute co-located if alleles are the same" 
    inputBinding:
        prefix: --check_alleles

  check_frequency:
    type: boolean?
    label: "Check frequency" 
    doc: "enable frequency checking" 
    inputBinding:
        prefix: --check_frequency

  gmaf:
    type: boolean?
    label: "Global MAF" 
    doc: "add global MAF of existing var" 
    inputBinding:
        prefix: --gmaf

  maf_1kg:
    type: boolean?
    label: "MAF 1000 Genomes" 
    doc: "add 1KG MAFs of existing vars" 
    inputBinding:
        prefix: --maf_1kg

  maf_esp:
    type: boolean?
    label: "MAF ESP" 
    doc: "add ESP MAFs of existing vars" 
    inputBinding:
        prefix: --maf_esp

  maf_exac:
    type: boolean?
    label: "MAF ExAC" 
    doc: "add ExAC MAFs of existing vars" 
    inputBinding:
        prefix: --maf_exac

  phased:
    type: boolean?
    label: "Phased" 
    doc: "force VCF genotypes to be interpreted as phased" 
    inputBinding:
        prefix: --phased

  fork:
    type: int 
    default: 1 
    label: "Fork" 
    doc: "fork into N processes" 
    inputBinding:
        prefix: --fork

  dont_skip:
    type: boolean?
    label: "Don't skip" 
    doc: "don't skip vars that fail validation" 
    inputBinding:
        prefix: --dont_skip

  verbose:
    type: boolean?
    label: "Verbose" 
    doc: "print out a bit more info while running" 
    inputBinding:
        prefix: --verbose

  quiet:
    type: boolean?
    label: "Quiet" 
    doc: "print nothign to STDOUT (unless using -o stdout)" 
    inputBinding:
        prefix: --quiet

  no_progress:
    type: boolean?
    label: "No progress bar" 
    doc: "don't display progress bars" 
    inputBinding:
        prefix: --no_progress

  everything:
    type: boolean?
    label: "Everything" 
    doc: "switch on EVERYTHING" 
    inputBinding:
        prefix: --everything

  canonical:
    type: boolean?
    label: "Canonical" 
    doc: "indicates if transcript is canonical" 
    inputBinding:
        prefix: --canonical

  tsl:
    type: boolean?
    label: "TSL" 
    doc: "output transcript support level" 
    inputBinding:
        prefix: --tsl

  appris:
    type: boolean?
    label: "APPRIS" 
    doc: "output APPRIS transcript annotation" 
    inputBinding:
        prefix: --appris

  ccds:
    type: boolean?
    label: "CCDS" 
    doc: "output CCDS identifier" 
    inputBinding:
        prefix: --ccds

  xref_refseq:
    type: boolean?
    label: "XREF RefSeq" 
    doc: "output refseq mrna xref" 
    inputBinding:
        prefix: --xref_refseq

  uniprot:
    type: boolean?
    label: "UniProt" 
    doc: "output Uniprot identifiers (includes UniParc)" 
    inputBinding:
        prefix: --uniprot

  protein:
    type: boolean?
    label: "Protein" 
    doc: "add e! protein ID to extra column" 
    inputBinding:
        prefix: --protein

  biotype:
    type: boolean?
    label: "Biotype" 
    doc: "add biotype of transcript to output" 
    inputBinding:
        prefix: --biotype

  hgnc:
    type: boolean?
    label: "HGNC ID" 
    doc: "add HGNC gene ID to extra column" 
    inputBinding:
        prefix: --hgnc

  symbol:
    type: boolean?
    label: "Gene Symbol" 
    doc: "add gene symbol (e.g., HGNC)" 
    inputBinding:
        prefix: --symbol

  gene_phenotype:
    type: boolean?
    label: "Gene phenotype" 
    doc: "indicates if genes are phenotype-associated" 
    inputBinding:
        prefix: --gene_phenotype

  hgvs:
    type: boolean?
    label: "HGVS" 
    doc: "add HGVS names to extra column" 
    inputBinding:
        prefix: --hgvs

  shift_hgvs:
    type: int?
    label: "Shift HGVS" 
    doc: "disable/enable 3-prime shifting of HGVS indels to comply with standard" 
    inputBinding:
        prefix: --shift_hgvs

  sift:
    type: string?
    label: "SIFT" 
    doc: "SIFT predictions" 
    inputBinding:
        prefix: --sift

  polyphen:
    type: string?
    label: "PolyPhen" 
    doc: "PolyPhen predictions" 
    inputBinding:
        prefix: --polyphen

  humdiv:
    type: boolean?
    label: "humdiv" 
    doc: "use humDiv instead of humVar for PolyPhen" 
    inputBinding:
        prefix: --humdiv

  condel:
    type: boolean?
    label: "Condel" 
    doc: "Condel predictions" 
    inputBinding:
        prefix: --condel

  variant_class:
    type: boolean?
    label: "Variant class" 
    doc: "get SO variant type" 
    inputBinding:
        prefix: --variant_class

  regulatory:
    type: boolean?
    label: "Regulatory" 
    doc: "enable regulatory stuff" 
    inputBinding:
        prefix: --regulatory

  no_intergenic:
    type: boolean?
    label: "No intergenic" 
    doc: "don't print out INTEGENIC consequences" 
    inputBinding:
        prefix: --no_intergenic

  domains:
    type: boolean?
    label: "Domains" 
    doc: "output overlapping protein features" 
    inputBinding:
        prefix: --domains

  numbers:
    type: boolean?
    label: "Numbers" 
    doc: "include exon and intron numbers" 
    inputBinding:
        prefix: --numbers

  total_length:
    type: boolean?
    label: "Total length" 
    doc: "give total length alongside positions e.g., 14/203" 
    inputBinding:
        prefix: --total_length

  allele_number:
    type: boolean?
    label: "Allele number" 
    doc: "indicate allele by number to avoid confusion with VCF conversions" 
    inputBinding:
        prefix: --allele_number

  no_escape:
    type: boolean?
    label: "No escape" 
    doc: "don't percent-escape HGVS strings" 
    inputBinding:
        prefix: --no_escape

  cache_version:
    type: string
    default: "84"
    label: "Cache version" 
    doc: "specify a different cache version" 
    inputBinding:
        prefix: --cache_version

  plugin:
    type: 
      type: array
      items: string
      inputBinding: 
        prefix: "--plugin"
    default: null
    label: "Plugin options" 
    doc: "specify a method in a module in the plugins directory. use multiple times if needed" 

  gdc_entrez:
    type: File?
    doc: "if you want to use the GDC_entrez plugin, the path to the json file"
    inputBinding:
        prefix: "--plugin"
        valueFrom: "$(self ? 'GDC_entrez,' + self.path : null)"

  gdc_evidence:
    type: File?
    doc: "if you want to use the GDC_evidence plugin, the path to the tabix-indexed variation vcf"
    inputBinding:
        prefix: "--plugin"
        valueFrom: "$(self ? 'GDC_evidence,' + self.path : null)"
    secondaryFiles:
        - ".tbi"

  fields:
    type: string?
    label: "Fields" 
    doc: "Configure the output format using a comma separated list of fields. Fields may be those present in the default output columns, or any of those that appear in the Extra column (including those added by plugins or custom annotations)."
    inputBinding:
        prefix: --fields

outputs:
  vep_out:
    type: File
    doc: "annotated output file"
    outputBinding:
        glob: $(inputs.output_file)

  stats_file:
    type: File? 
    doc: "statistics file"
    outputBinding:
        glob: $(inputs.stats_filename)

  warning_file:
    type: File? 
    doc: "warnings file"
    outputBinding:
        glob: $(inputs.warning_filename)

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
      glob: $(inputs.output_file.substr(0, inputs.output_file.lastIndexOf('.')) + '.time.json')
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

  - valueFrom: $(inputs.output_file.substr(0, inputs.output_file.lastIndexOf('.')) + '.time.json')
    position: -9
    prefix: -o

  - valueFrom: "variant_effect_predictor.pl"
    position: -8

  - valueFrom: "--offline"
    position: -7

  - valueFrom: "--cache"
    position: -6

  - valueFrom: "--force_overwrite"
    position: -5
