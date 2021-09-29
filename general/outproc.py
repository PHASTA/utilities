#!/usr/bin/env python3

import argparse
from pathlib import Path
import re
from statistics import stdev
import warnings

numRe = r'[+-]?(?:0|[1-9]\d*)(?:\.\d*)?(?:[eE][+\-]?\d+)' # scientific notation regex
iterationRe = re.compile(r'\s*(?P<timestep>\d+)\s+(?P<walltime>{0})\s+(?P<residual>{0})\s+'
                         r'\((?P<decibel>.*)\)\s+(?P<vel_res>{0})\s+(?P<pre_res>{0})\s*'
                         r'<\s*(?P<maxres_node>\d+)\s*-\s*(?P<maxres_part>\d+)\s*'
                         r'\|\s*(?P<maxres_ratio>\d+)\s*>\s*'
                         r'\[\s*(?P<CGiter>\d+)\s*-\s*(?P<GMRESiter>\d+)\s*\]'.format(numRe))

def parseIterLine(line):
    """Parse line for PHASTA iteration information

    Returns dictionary of the matches converted to a numeric type (either int
    or float).
    """

    keyTypeDict = {
   'timestep':     int,
   'walltime':     float,
   'residual':     float,
   'decibel':      int,
   'vel_res':      float,
   'pre_res':      float,
   'maxres_node':  int,
   'maxres_part':  int,
   'maxres_ratio': int,
   'GMRESiter':    int,
   'CGiter':       int,
    }

    match = iterationRe.search(line)
    if match:
        matchdict = match.groupdict()
        for key, dtype in keyTypeDict.items():
            matchdict[key] = dtype(matchdict[key])
    else:
        matchdict = None

    return matchdict


def parseOutFile(file):
    """Parse the file and return list of dictionaries of the results

    file : pathlib.PurePath
        Path to the file to be parsed
    """
    with file.open() as fileread:
        output = fileread.readlines()

    iterations = []
    for line in output:
        matchdict = parseIterLine(line)
        if matchdict:
            iterations.append(matchdict)

    return iterations


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Get timestep statistics from PHASTA output files.',
                                     prog='outproc')
    parser.add_argument('output', help='Path to PHASTA output file', type=Path)
    parser.add_argument('-t', '--time',
                        help='Calculate # of timesteps that can be run in TIME number of hours',
                        type=float)
    parser.add_argument('-s', '--stddev',
                        help='Calculate standard deviation. '
                            + 'Probably inaccurate due to PHASTA limiting significant digits',
                        action='store_const', const=True)

    args = parser.parse_args()
    if not args.output.exists():
        parser.error('PHASTA output file "{}" does not exist!'.format(args.output.as_posix()))

    iterations = parseOutFile(args.output)
    if not iterations:
        raise EOFError('No timestep information could be parsed '
                       'from the file: {}'.format(args.output.as_posix()))

    print('Starting timestep: {}'.format(iterations[0]['timestep']))
    print('Ending timestep:   {}'.format(iterations[-1]['timestep']))
    average = (iterations[-1]['walltime'] - iterations[0]['walltime'])/ \
              (iterations[-1]['timestep'] - iterations[0]['timestep'])
    print('Seconds per timestep: ' + str(average))

    if args.stddev:
        tsTime = []
        timestep0 = iterations[0]['timestep']
        walltime0 = iterations[0]['walltime']
        for iteration in iterations:
            if iteration['timestep'] == timestep0:
                continue
            else:
                tsTime.append(walltime0 - iteration['walltime'])
                timestep0 = iteration['timestep']
                walltime0 = iteration['walltime']

        stddev = stdev(tsTime)

        print('\t!Warning!: Standard deviation is probably innaccurate due to ' +
              '\n\ttruncation of time reported by PHASTA')

        print('Standard Deviation of timestep duration: ' + str(stddev))

    if args.time:
        tsInJob = (args.time*60**2)/average
        print('Timesteps in job: ' + str(tsInJob))
        print('\t rerun-check: ' + str(tsInJob+iterations[0]['timestep']))
