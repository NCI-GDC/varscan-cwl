import os
import sys
import subprocess
import logging
import time
import shutil

def run_command(cmd, logger=None, shell_var=False):
    """ Run a subprocess command """

    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell_var)
    stdoutdata, stderrdata = child.communicate()
    exit_code = child.returncode

    if logger != None:
        logger.info(cmd)
        stdoutdata = stdoutdata.split("\n")
        for line in stdoutdata:
            logger.info(line)

        stderrdata = stderrdata.split("\n")
        for line in stderrdata:
            logger.info(line)

    return exit_code

def download_from_cleversafe(logger, remote_input, local_output, config="/home/ubuntu/.s3cfg"):
    """ Download a file from cleversafe to a local folder """

    if (remote_input != ""):
        cmd = ['s3cmd', '-c', config, 'sync', remote_input, local_output]
        exit_code = run_command(cmd, logger)
    else:
        raise Exception("invalid input %s" % remote_input)

    return exit_code

def upload_to_cleversafe(logger, remote_output, local_input, config="/home/ubuntu/.s3cfg"):
    """ Upload a file to cleversafe to a folder """

    if (remote_output != "" and (os.path.isfile(local_input) or os.path.isdir(local_input))):
        cmd = ['s3cmd', '-c', config, 'sync', local_input, remote_output]
        exit_code = run_command(cmd, logger)
    else:
        raise Exception("invalid input %s or output %s" %(local_input, remote_output))

    return exit_code

def remove_dir(dirname):
    """ Remove a directory and all it's contents """

    if os.path.isdir(dirname):
        shutil.rmtree(dirname)
    else:
        raise Exception("Invalid directory: %s" % dirname)
