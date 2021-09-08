#!/usr/bin/env bash

RS="\033[0m"    # reset
UL="\033[4m"    # underline

USAGE="
Report PBS log for PBSJOBID using tracejob

${UL}Usage:${RS} tracejobssh [-e] [PBSJOBID]

${UL}Options:${RS}

-e      Use when checking a job running on Endeavour

${UL}Description:${RS}

Running 'tracejob' requires sshing into pbspl1 (or pbspl3 for Endeavour jobs).
This utility sshs to the appropriate server runs the command, and returns the
output.

When run without arguments (ie. 'tracejobssh'), the script will look for queued
jobs of the current user and run 'tracejob' on them.
"

OTHER_ARGUMENTS=()
for arg in "$@"
do
    case $arg in
        -h | --help)
            echo -e "$USAGE"
            exit 0
            ;;
        -e)
            ENDEAVOUR=1
            shift
            ;;
        *)
            OTHER_ARGUMENTS+=( "$1" )
            shift
            ;;
    esac
done

if [ -z $OTHER_ARGUMENTS ]; then
    Jobs=($(qstat -u $USER -W o=JobID -W o=+S | awk '$2 !~ /H/ {print $1}'))
    if [ -z $Jobs ]; then
        echo "No queued jobs from ${USER} (jobs either running, held, or not submitted)."
        exit 0
    fi
    for job in ${Jobs[@]}; do
        SSH_ARGS="${SSH_ARGS}tracejob ${job}; "
    done
    echo 'Jobs:' $Jobs
else
    SSH_ARGS="tracejob ${OTHER_ARGUMENTS}"
fi

echo 'SSH_ARGS:'${SSH_ARGS}

if [ $ENDEAVOUR ]; then
    ssh pbspl3 "${SSH_ARGS}"
else
    ssh pbspl1 "${SSH_ARGS}"
fi
