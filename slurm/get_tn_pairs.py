import postgres
import argparse
import os


if __name__ == "__main__":


    parser = argparse.ArgumentParser(description="Variant calling using Somatic-Sniper")

    required = parser.add_argument_group("Required input parameters")
    required.add_argument("--config", default=None, help="path to config file", required=True)
    required.add_argument("--outdir", default="./", help="otuput directory for slurm scripts")
    args = parser.parse_args()

    if not os.path.isdir(args.outdir):
        raise Exception("Cannot find output directory: %s" %args.outdir)

    if not os.path.isfile(args.config):
        raise Exception("Cannot find config file: %s" %args.config)


    s = open(args.config, 'r').read()
    config = eval(s)

    DATABASE = {
        'drivername': 'postgres',
        'host' : 'pgreadwrite.osdc.io',
        'port' : '5432',
        'username': config['username'],
        'password' : config['password'],
        'database' : 'prod_bioinfo'
    }

    engine = postgres.db_connect(DATABASE)

    count_host = 0
    cases = postgres.get_case(engine, 'varscan_status')

    for case in cases:
        slurm = open(os.path.join(args.outdir, "vs.%s.%s.sh" %(cases[case][1], cases[case][3])), "w")
        temp = open("template.sh", "r")
        for line in temp:
            if "XX_NORMAL_XX" in line:
                line = line.replace("XX_NORMAL_XX", cases[case][2])

            if "XX_TUMOR_XX" in line:
                line = line.replace("XX_TUMOR_XX", cases[case][4])

            if "XX_NORMAL_ID_XX" in line:
                line = line.replace("XX_NORMAL_ID_XX", cases[case][1])

            if "XX_TUMOR_ID_XX" in line:
                line = line.replace("XX_TUMOR_ID_XX", cases[case][3])

            if "XX_CASE_ID_XX" in line:
                line = line.replace("XX_CASE_ID_XX", cases[case][0])

            if "XX_username_XX" in line:
                line = line.replace("XX_username_XX", config['username'])

            if "XX_password_XX" in line:
                line = line.replace("XX_password_XX", config['password'])

            if "XX_HOST_BASE_XX" in line:
                if count_host % 2 == 0:
                    line = line.replace("XX_HOST_BASE_XX", '$host_base_kh11')
                else:
                    line = line.replace("XX_HOST_BASE_XX", '$host_base_kh13')

            slurm.write(line)
        count_host += 1
        slurm.close()
        temp.close()
