import os
import datetime
import json
import gzip
import time
import subprocess

import postgres.utils
import postgres.vcf_status
import utils.s3
import utils.pipeline
import utils.helpers

class VarscanIndelOneoffTool(object):
    def __init__(self, workdir, inputdir, refdir, resource_json_file, 
                 hostname, program, project, case_id, src_vcf_id, 
                 tumor_bam_id, normal_bam_id, raw_vcf_id, annotated_vcf_id,
                 hc_snp_vcf, raw_indel_vcf, biasfiltered_vcf, tumor_bam, 
                 tumor_index, python_exe, script_path, s3dir, threads, 
                 logger, cwl_tool):
        # Main inputs
        self.workdir            = workdir
        self.inputdir           = inputdir
        self.refdir             = refdir
        self.resource_json_file = resource_json_file
        self.hostname           = hostname
        self.program            = program
        self.project            = project
        self.case_id            = case_id
        self.src_vcf_id         = src_vcf_id
        self.tumor_bam_id       = tumor_bam_id
        self.normal_bam_id      = normal_bam_id
        self.raw_vcf_id         = raw_vcf_id
        self.annotated_vcf_id   = annotated_vcf_id
        self.hc_snp_vcf         = hc_snp_vcf
        self.raw_indel_vcf      = raw_indel_vcf
        self.biasfiltered_vcf   = biasfiltered_vcf
        self.tumor_bam          = tumor_bam
        self.tumor_index        = tumor_index
        self.python_exe         = python_exe
        self.script_path        = script_path 
        self.s3dir              = s3dir
        self.threads            = threads
        self.logger             = logger
        self.cwl_tool           = cwl_tool

        # Resources
        self.resource_data      = utils.helpers.load_json_from_file(self.resource_json_file)
        self.pg_config          = os.path.join(refdir, self.resource_data['pg_config']) 

        # Times
        self.cwl_start          = None
        self.cwl_end            = None
        self.datetime_now       = str(datetime.datetime.now())

        # Input/output JSON
        self.input_json_file    = os.path.join(workdir, '{0}.varscan_indel_oneoff.inputs.json'.format(
             raw_vcf_id))
        self.out_json_file      = os.path.join(workdir, '{0}.varscan_indel_oneoff.outputs.json'.format(
             raw_vcf_id))
        self.input_json_data    = self._create_input_json_data()
        self.out_json_data      = None

        # Postgres table classes
        self.status_class       = postgres.vcf_status.VcfStatus

        # CWL status
        self.cwl_failure        = False

        # S3 status
        self.s3profile    = "ceph" if "ceph" in self.s3dir else "cleversafe"
        self.s3endpoint   = "http://gdc-cephb-objstore.osdc.io/" if self.s3profile == "ceph" \
            else "http://gdc-accessors.osdc.io/"
        self.s3put_status       = None

        # Output basics
        self.upload_directory             = os.path.join(self.s3dir, self.raw_vcf_id)
        self.raw_vcf_filename             = '{0}.vcf.gz'.format(self.raw_vcf_id)
        self.raw_vcf_index_filename       = '{0}.vcf.gz.tbi'.format(self.raw_vcf_id)
        self.annotated_vcf_filename       = '{0}.vep.vcf.gz'.format(self.annotated_vcf_id)
        self.annotated_vcf_index_filename = '{0}.vep.vcf.gz.tbi'.format(self.annotated_vcf_id)

        # postgres data object
        self.pg_data = {
          "job_id": os.environ.get("SLURM_JOBID"),
          "program": program,
          "project": project,
          "case_id": self.case_id,
          "tumor_bam_uuid": self.tumor_bam_id,
          "normal_bam_uuid": self.normal_bam_id,
          "status": None,
          "src_vcf_id": self.src_vcf_id,
          "location": self.upload_directory,
          "raw_vcf_filename": self.raw_vcf_filename,
          "raw_vcf_index_filename": self.raw_vcf_index_filename,
          "raw_vcf_id": self.raw_vcf_id,
          "raw_md5": ["UNKNOWN", "UNKNOWN"],
          "annotated_vcf_filename": self.annotated_vcf_filename,
          "annotated_vcf_index_filename": self.annotated_vcf_index_filename,
          "annotated_vcf_id": self.annotated_vcf_id,
          "annotated_md5": ["UNKNOWN", "UNKNOWN"],
          "datetime_now": self.datetime_now, 
          "hostname": self.hostname,
          "docker": self.resource_data['docker'],
          "thread_count": self.threads,
          "elapsed": None
        }

    def run(self):
        """
        Main function for running the tool.
        """
        self.cwl_start = time.time()

        ## Download inputs 
        self._download_all_inputs()

        ## CWL
        os.chdir(self.workdir)

        self.logger.info("running CWL workflow")
        cmd = [
            '/home/ubuntu/.virtualenvs/p2/bin/cwltool',
            '--debug',
            '--outdir', self.workdir,
            '--tmpdir-prefix', self.inputdir,
            '--tmp-outdir-prefix', self.workdir,
            self.cwl_tool,
            self.input_json_file
        ] 

        # run cwl
        self.logger.info(cmd)
        child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdoutdata, stderrdata = child.communicate()
        cwl_exit = child.returncode
        with open(self.out_json_file, 'wt') as o:
            o.write(stdoutdata)
        for line in stderrdata.split("\n"):
            self.logger.info(line)

        # cwl failure status
        if cwl_exit:
            self.cwl_failure = True

        # Upload results
        self._upload_results()

        # Out json data
        self.out_json_data = utils.helpers.load_json_from_file(self.out_json_file)

        ## Metrics
        self.cwl_end            = time.time()
        self.pg_data['elapsed'] = self.cwl_end - self.cwl_start

        ## CWL pass
        if not self.cwl_failure:
            self._process_cwl_ok()
        else:
            self._process_cwl_fail()

        ## Update tables
        engine = postgres.utils.get_db_engine(self.pg_config)
        postgres.vcf_status.add_vcf_status(engine, self.status_class, self.pg_data)

        ## Cleanup
        utils.pipeline.remove_dir(self.workdir)

    def _process_cwl_ok(self):
        raw_vcf_local           = os.path.join(self.workdir, self.raw_vcf_filename)
        raw_vcf_idx_local       = os.path.join(self.workdir, self.raw_vcf_index_filename)
        annotated_vcf_local     = os.path.join(self.workdir, self.annotated_vcf_filename)
        annotated_vcf_idx_local = os.path.join(self.workdir, self.annotated_vcf_index_filename)
        
        if self.s3put_status == 0:
            self.pg_data['status'] = 'COMPLETED'
            self.logger.info("uploaded all files to object store. The path is: {}".format(
                self.upload_directory))
            # Update md5
            self.pg_data['raw_md5'] = [utils.pipeline.get_md5(i) for i in [raw_vcf_local, raw_vcf_idx_local]]
            self.pg_data['annotated_md5'] = [utils.pipeline.get_md5(i) for i in [annotated_vcf_local, annotated_vcf_idx_local]]
        else:
            self.pg_data['status'] = 'UPLOAD_FAILURE'
            self.pg_data['location'] = 'Not Applicable'
            self.logger.info("Upload of files failed")

    def _process_cwl_fail(self):
        ## check s3put code
        if self.s3put_status == 0:
            self.pg_data['status'] = 'CWL_FAILED'
            self.logger.info("CWL failed but outputs were generated. The path is: {}".format(
                self.upload_directory))
        else:
            self.pg_data['status'] = 'FAILED'
            self.pg_data['location'] = 'Not Applicable'
            self.logger.info("CWL and upload both failed")

    def _download_all_inputs(self):
        dat = [
            {'key': 'hc_snp_vcf', 
             'localpath': self.input_json_data['hc_snp_vcf']['path'], 
             'fpath': self.hc_snp_vcf,
             'objectstore': "ceph" if self.hc_snp_vcf.startswith('s3://washu_varscan_variant') \
                 or self.hc_snp_vcf.startswith('s3://ceph') else "cleversafe",
             'download_error': "VCF_DOWNLOAD_ERROR",
             'size_zero_error': "VCF_SIZE_ZERO_ERROR",
             'gz_decompress': True},
            {'key': 'raw_indel_vcf', 
             'localpath': self.input_json_data['raw_indel_vcf']['path'], 
             'fpath': self.raw_indel_vcf,
             'objectstore': "ceph" if self.raw_indel_vcf.startswith('s3://washu_varscan_variant') \
                 or self.raw_indel_vcf.startswith('s3://ceph') else "cleversafe",
             'download_error': "VCF_DOWNLOAD_ERROR",
             'size_zero_error': "VCF_SIZE_ZERO_ERROR",
             'gz_decompress': True},
            {'key': 'varscan_biasfiltered_vcf', 
             'localpath': self.input_json_data['varscan_biasfiltered_vcf']['path'], 
             'fpath': self.biasfiltered_vcf,
             'objectstore': "ceph" if self.biasfiltered_vcf.startswith('s3://ceph') else "cleversafe",
             'download_error': "VCF_DOWNLOAD_ERROR",
             'size_zero_error': "VCF_SIZE_ZERO_ERROR",
             'gz_decompress': False},
            {'key': 'tumor_bam', 
             'localpath': self.input_json_data['tumor_bam']['path'], 
             'fpath': self.tumor_bam,
             'objectstore': "ceph" if self.tumor_bam.startswith('s3://ceph') else "cleversafe",
             'download_error': "BAM_DOWNLOAD_ERROR",
             'size_zero_error': "BAM_SIZE_ZERO_ERROR",
             'gz_decompress': False},
            {'key': 'tumor_index', 
             'localpath': self.input_json_data['tumor_index']['path'], 
             'fpath': self.tumor_index,
             'objectstore': "ceph" if self.tumor_index.startswith('s3://ceph') else "cleversafe",
             'download_error': "BAI_DOWNLOAD_ERROR",
             'size_zero_error': "BAI_SIZE_ZERO_ERROR",
             'gz_decompress': False}
        ]

        for d in dat:
            self._get_input_file(**d)

    def _get_input_file(self, key, localpath, fpath, objectstore, download_error, size_zero_error, gz_decompress=False):
        if not os.path.isfile(localpath):
            self.logger.info("getting {0}: {1}".format(key, fpath))
            exit_code = None
            if objectstore == 'ceph':
                exit_code = utils.s3.aws_s3_get(self.logger, fpath, self.inputdir,
                    "ceph", "http://gdc-cephb-objstore.osdc.io/",
                    recursive=False)
            else:
                exit_code = utils.s3.aws_s3_get(self.logger, fpath, self.inputdir,
                    "cleversafe", "http://gdc-accessors.osdc.io/",
                    recursive=False)
            if exit_code != 0:
                self.logger.warn("Error downloading {0}: {1}".format(key, fpath))
                self._handle_download_error(download_error)
                raise Exception(download_error)
            elif not os.path.isfile(os.path.join(self.inputdir, os.path.basename(fpath))):
                self.logger.warn("Can't find downloaded file {0}: {1}".format(key, fpath)) 
                self._handle_download_error(download_error)
                raise Exception(download_error + ' cant find file')
            elif utils.pipeline.get_file_size(os.path.join(self.inputdir, os.path.basename(fpath))) == 0:
                self.logger.warn("Zero size file {0}".format(self.fpath))
                self._handle_download_error(size_zero_error)
                raise Exception(size_zero_error)

            # decompress
            if gz_decompress and fpath.endswith('.gz'):
                self.logger.info("Decompressing {0}".format(key))
                try:
                    ifil = os.path.join(self.inputdir, os.path.basename(fpath))
                    with open(localpath, 'wt') as o:
                        for line in gzip.open(ifil, 'rt'):
                            o.write(line) 
                except Exception, e:
                    self.logger.warn("Error decompressing {0}".format(key))
                    self._handle_download_error("VCF_GUNZIP_ERROR")
                    raise e 

    def _handle_download_error(self, status):
        self.cwl_end = time.time()
        self.pg_data['status']   = status
        self.pg_data['location'] = None
        self.pg_data['elapsed']  = self.cwl_end - self.cwl_start
        self.pg_data['raw_vcf_filename'] = None
        self.pg_data['raw_vcf_index_filename'] = None
        self.pg_data['annotated_vcf_filename'] = None
        self.pg_data['annotated_vcf_index_filename'] = None
        engine = postgres.utils.get_db_engine(self.pg_config)
        # status
        postgres.vcf_status.add_vcf_status(engine, self.status_class, self.pg_data)
        # cleanup
        utils.pipeline.remove_dir(self.workdir)

    def _upload_results(self):
        self.logger.info("Uploaded to s3")
        self.s3put_status = utils.s3.aws_s3_put(
            self.logger, self.upload_directory, self.workdir,
            self.s3profile, self.s3endpoint)

    def _create_input_json_data(self):
        hc_snp_vcf = os.path.splitext(os.path.basename(self.hc_snp_vcf))[0] \
            if self.hc_snp_vcf.endswith(".gz") \
            else os.path.basename(self.hc_snp_vcf)

        raw_indel_vcf = os.path.splitext(os.path.basename(self.raw_indel_vcf))[0] \
            if self.raw_indel_vcf.endswith(".gz") \
            else os.path.basename(self.raw_indel_vcf)

        dat = {
          "hc_snp_vcf": {
            "class": "File",
            "path": os.path.join(self.inputdir, hc_snp_vcf)
          },
          "raw_indel_vcf": {
            "class": "File",
            "path": os.path.join(self.inputdir, raw_indel_vcf)
          },
          "varscan_biasfiltered_vcf": {
            "class": "File",
            "path": os.path.join(self.inputdir, os.path.basename(self.biasfiltered_vcf))
          },
          "tumor_bam": {
            "class": "File",
            "path": os.path.join(self.inputdir, os.path.basename(self.tumor_bam))
          },
          "tumor_index": {
            "class": "File",
            "path": os.path.join(self.inputdir, os.path.basename(self.tumor_index))
          },
          "raw_uuid": self.raw_vcf_id,
          "annotated_uuid": self.annotated_vcf_id,
          "vep_forks": self.threads,
          "python": self.python_exe,
          "script": self.script_path,
          "full_sequence_dictionary": {
            "class": "File",
            "path": os.path.join(self.refdir, self.resource_data["full_sequence_dictionary"])
          },
          "full_reference_fasta": {
            "class": "File",
            "path": os.path.join(self.refdir, self.resource_data["full_reference_fasta"])
          },
          "main_reference_fai": {
            "class": "File",
            "path": os.path.join(self.refdir, self.resource_data["main_reference_fai"])
          },
          "main_sequence_dictionary": {
            "class": "File",
            "path": os.path.join(self.refdir, self.resource_data["main_sequence_dictionary"])
          },
          "vep_fasta": {
            "class": "File",
            "path": os.path.join(self.refdir, self.resource_data["vep_fasta"])
          },
          "cache": {
            "class": "Directory",
            "path": os.path.join(self.refdir, self.resource_data["cache"])
          },
          "gdc_entrez": {
            "class": "File",
            "path": os.path.join(self.refdir, self.resource_data["gdc_entrez"])
          },
          "gdc_evidence": {
            "class": "File",
            "path": os.path.join(self.refdir, self.resource_data["gdc_evidence"])
          }
        }
        with open(self.input_json_file, 'wt') as o:
            json.dump(dat, o, indent=4)
        return dat
