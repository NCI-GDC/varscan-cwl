"""Module for running commands, getting file stats, and
setting up logging.
"""
import logging
import hashlib
import subprocess
import os
import shutil

def setup_logging(log_name, log_filename=None):
    """ 
    Sets up a logger
    """
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)

    if log_filename is None:
        ch = logging.StreamHandler()
    else:
        ch = logging.FileHandler(log_filename, mode='w')

    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)s] [%(asctime)s] [%(name)s] - %(message)s',
                                  datefmt='%H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

def get_md5(input_file):
    '''Estimates md5 of file '''
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(input_file, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)
    return hasher.hexdigest()

def get_file_size(filename):
    ''' Gets file size '''
    fstats = os.stat(filename)
    return fstats.st_size

def run_command(cmd, logger=None, shell_var=False):
    '''
    Runs a subprocess
    '''
    child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=shell_var)
    stdoutdata, stderrdata = child.communicate()
    exit_code = child.returncode

    if logger is not None:
        logger.info(cmd)
        stdoutdata = stdoutdata.split("\n")
        for line in stdoutdata:
            logger.info(line)

        stderrdata = stderrdata.split("\n")
        for line in stderrdata:
            logger.info(line)

    return exit_code

def remove_dir(dirname):
    """ Remove a directory and all it's contents """

    if os.path.isdir(dirname):
        shutil.rmtree(dirname)
    else:
        raise Exception("Invalid directory: %s" % dirname)
