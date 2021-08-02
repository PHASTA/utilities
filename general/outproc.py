#!/usr/bin/env python3

import argparse
from pathlib import Path
import re
from statistics import stdev
import warnings

def parseOutFile(file):
    laststepRe = re.compile(r'^\s*stopjob(?:\S+\s+){2}(\d+)\s+(\d+)')
    solTimeRe = re.compile(r'^\s*\d+\s+(\S+)')

    with file.open() as fileread:
        output = fileread.readlines()

    laststepBool = False
    times = []
    timesteps = []
    for i, line in enumerate(output):
        laststepMatch = laststepRe.match(line)
        if laststepMatch:
            laststepBool = True
            timestep = laststepMatch.group(1)
            continue
        if laststepBool:
            solTimeMatch = solTimeRe.match(line)
            if solTimeMatch:
                times.append(float(solTimeMatch.group(1)))
                timesteps.append(int(timestep))
            else:
                warnings.warn('Did not find solution wall-time at line {}:\n\t "{}"'.format(i, line.rstrip()))
                print()
            laststepBool = False

    return times, timesteps

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

    times, timesteps = parseOutFile(args.output)
    print('Starting timestep: {}'.format(timesteps[0]))
    print('Ending timestep:   {}'.format(timesteps[-1]))
    average = (times[-1] - times[0])/(timesteps[-1] - timesteps[0])
    print('Seconds per timestep: ' + str(average))

    if args.stddev:
        tsTime = []
        for i in range(len(times)-1):
            tsTime.append(times[i] - times[i+1])

        stddev = stdev(tsTime)

        print('\t!Warning!: Standard deviation is probably innaccurate due to ' +
              '\n\ttruncation of time reported by PHASTA')

        print('Standard Deviation of timestep duration: ' + str(stddev))

    if args.time:
        tsInJob = (args.time*60**2)/average
        print('Timesteps in job: ' + str(tsInJob))
        print('\t rerun-check: ' + str(tsInJob+timesteps[0]))
