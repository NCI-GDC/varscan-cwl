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
    (tumor, tumor_file, normal, normal_file) = postgres.get_complete_cases(engine)

    for case_id in tumor:
        for tum in tumor[case_id]:
            for norm in normal[case_id]:
                pair = [norm, tum]
                slurm = open(os.path.join(args.outdir, "vs.%s.%s.sh" %(norm, tum)), "w")
                temp = open("template.sh", "r")
                for line in temp:
                    if "XX_NORMAL_XX" in line:
                        line = line.replace("XX_NORMAL_XX", normal_file[norm])

                    if "XX_TUMOR_XX" in line:
                        line = line.replace("XX_TUMOR_XX", tumor_file[tum])

                    if "XX_NORMAL_ID_XX" in line:
                        line = line.replace("XX_NORMAL_ID_XX", norm)

                    if "XX_TUMOR_ID_XX" in line:
                        line = line.replace("XX_TUMOR_ID_XX", tum)

                    if "XX_CASE_ID_XX" in line:
                        line = line.replace("XX_CASE_ID_XX", case_id)

                    slurm.write(line)
                slurm.close()
                temp.close()

