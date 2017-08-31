import postgres.status
import postgres.utils
import argparse
import os
import utils.s3

def is_nat(x):
    '''
    Checks that a value is a natural number.
    '''
    if int(x) > 0:
        return int(x)
    raise argparse.ArgumentTypeError('%s must be positive, non-zero' % x)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="VarScan (v2.3.9) Pipeline SLURM script creator")
    required = parser.add_argument_group("Required input parameters")
    required.add_argument("--thread_count", help="Thread count", required=True)
    required.add_argument("--mem", help="Max mem for each node", required=True)
    required.add_argument("--refdir", help="Reference dir on node", required=True)
    required.add_argument("--s3dir", help="S3bin for uploading output files", required=True)
    required.add_argument("--block", help="Parallel block size", required=True)
    required.add_argument("--postgres_config", help="Path to postgres config file", required=True)
    required.add_argument("--outdir", default="./", help="Output directory for slurm scripts")
    required.add_argument("--input_table", help="Postgres input table name", required=True)
    required.add_argument("--input_primary_id", default="id", help="Primary id for postgres input table")
    required.add_argument("--status_table", default="None", help="Postgres status table name")
    args = parser.parse_args()

    if not os.path.isdir(args.outdir):
        raise Exception("Cannot find output directory: %s" % args.outdir)

    if not os.path.isfile(args.postgres_config):
        raise Exception("Cannot find config file: %s" % args.postgres_config)
    upload_s3 = utils.s3.check_s3url(args.s3dir)
    engine = postgres.utils.get_db_engine(args.postgres_config)
    cases = postgres.status.get_case(engine, str(args.input_table), str(args.status_table), input_primary_column=str(args.input_primary_id))
    for case in cases:
        tumor_s3 = utils.s3.check_s3url(cases[case][3])
        normal_s3 = utils.s3.check_s3url(cases[case][4])
        slurm = open(os.path.join(args.outdir, "varscan2.{}.sh".format(cases[case][0])), "w")
        template = os.path.join(os.path.dirname(os.path.realpath(__file__)),
        "etc/template.sh")
        temp = open(template, "r")
        for line in temp:
            if "XX_THREAD_COUNT_XX" in line:
                line = line.replace("XX_THREAD_COUNT_XX", str(args.thread_count))
            if "XX_MEM_XX" in line:
                line = line.replace("XX_MEM_XX", str(args.mem))
            if "XX_CASEID_XX" in line:
                line = line.replace("XX_CASEID_XX", str(cases[case][0]))
            if "XX_TID_XX" in line:
                line = line.replace("XX_TID_XX", str(cases[case][1]))
            if "XX_TS3URL_XX" in line:
                line = line.replace("XX_TS3URL_XX", tumor_s3['s3url'])
            if "XX_TS3PROFILE_XX" in line:
                line = line.replace("XX_TS3PROFILE_XX", tumor_s3['profile'])
            if "XX_TS3ENDPOINT_XX" in line:
                line = line.replace("XX_TS3ENDPOINT_XX", tumor_s3['endpoint'])
            if "XX_NID_XX" in line:
                line = line.replace("XX_NID_XX", str(cases[case][2]))
            if "XX_NS3URL_XX" in line:
                line = line.replace("XX_NS3URL_XX", normal_s3['s3url'])
            if "XX_NS3PROFILE_XX" in line:
                line = line.replace("XX_NS3PROFILE_XX", normal_s3['profile'])
            if "XX_NS3ENDPOINT_XX" in line:
                line = line.replace("XX_NS3ENDPOINT_XX", normal_s3['endpoint'])
            if "XX_REFDIR_XX" in line:
                line = line.replace("XX_REFDIR_XX", args.refdir)
            if "XX_S3DIR_XX" in line:
                line = line.replace("XX_S3DIR_XX", upload_s3['s3url'])
            if "XX_S3PROFILE_XX" in line:
                line = line.replace("XX_S3PROFILE_XX", upload_s3['profile'])
            if "XX_S3ENDPOINT_XX" in line:
                line = line.replace("XX_S3ENDPOINT_XX", upload_s3['endpoint'])
            if "XX_BLOCKSIZE_XX" in line:
                line = line.replace("XX_BLOCKSIZE_XX", str(args.block))
            slurm.write(line)
        slurm.close()
        temp.close()
