#!/usr/bin/env python
import os
import gzip
import argparse

if __name__ == '__main__':
   p = argparse.ArgumentParser("Filter SNP VCF")
   p.add_argument("input_vcf", type=str, help="The filtered and annotated VCF")
   p.add_argument("output_vcf", type=str, help="The output VCF file")
   args = p.parse_args()

   open_func = gzip.open if args.input_vcf.endswith('.gz') else open 
   with open(args.output_vcf, 'wt') as o:
       for line in open_func(args.input_vcf, 'rt'):
           if line.startswith('#'):
               if line.startswith('##INFO=<ID=CSQ') or line.startswith('##VEP'): continue
               o.write(line)
           else:
               cols = line.rstrip('\r\n').split('\t')
               info = [i for i in cols[7].split(';') if not i.startswith('CSQ=')]
               cols[7] = ';'.join(info) if info else '.' 
               o.write('\t'.join(cols) + '\n') 
